using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Diagnostics;

public static partial class WeChatDecryptProbe {
 public sealed class ProcessReadHandle : Microsoft.Win32.SafeHandles.SafeHandleZeroOrMinusOneIsInvalid {
  public ProcessReadHandle(IntPtr h):base(true){SetHandle(h);}
  protected override bool ReleaseHandle(){return CloseHandle(handle);}
 }
 [DllImport("advapi32.dll",SetLastError=true)] static extern bool OpenProcessToken(IntPtr process,uint access,out IntPtr token);
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool QueryFullProcessImageName(IntPtr process,int flags,StringBuilder name,ref int size);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool IsWow64Process(IntPtr process,out bool wow64);
 public static string ValidatedVersion(IntPtr h) {
  var path=new StringBuilder(32768);int size=path.Capacity;
  if(!QueryFullProcessImageName(h,0,path,ref size)||!Path.GetFileName(path.ToString()).Equals("Weixin.exe",StringComparison.OrdinalIgnoreCase))throw new Exception("Target process is not Weixin");
  string version=FileVersionInfo.GetVersionInfo(path.ToString()).FileVersion;
  if(version!="4.1.15.56")throw new Exception("Unsupported WeChat runtime layout");return version;
 }
 public static ProcessReadHandle OpenAuthorizedProcess(int pid) {
  if(IntPtr.Size!=8||!Environment.Is64BitOperatingSystem)throw new Exception("Windows x64 required");
  var h=new ProcessReadHandle(OpenProcess(0x410,false,pid));
  try {
   if(h.IsInvalid)throw new Exception("Read-only process access denied");
   IntPtr raw=h.DangerousGetHandle();bool wow64;
   if(!IsWow64Process(raw,out wow64)||wow64)throw new Exception("Target must be x64");
   IntPtr token;
   if(!OpenProcessToken(raw,8,out token))throw new Exception("Cannot query process owner");
   try {using(var owner=new WindowsIdentity(token))using(var self=WindowsIdentity.GetCurrent())
    if(!owner.User.Equals(self.User))throw new Exception("Different Windows process owner rejected");
   } finally {CloseHandle(token);}
   ValidatedVersion(raw);return h;
  } catch {h.Dispose();throw;}
 }
 [DllImport("kernel32.dll", SetLastError=true)] static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
 [DllImport("kernel32.dll", SetLastError=true)] static extern bool CloseHandle(IntPtr h);
 [DllImport("kernel32.dll", SetLastError=true)] static extern UIntPtr VirtualQueryEx(IntPtr h, UIntPtr addr, out MBI info, UIntPtr size);
 [DllImport("kernel32.dll", SetLastError=true)] static extern bool ReadProcessMemory(IntPtr h, UIntPtr addr, byte[] buffer, UIntPtr count, out UIntPtr read);
 [StructLayout(LayoutKind.Sequential)] struct MBI { public UIntPtr BaseAddress; public UIntPtr AllocationBase; public uint AllocationProtect; public UIntPtr RegionSize; public uint State; public uint Protect; public uint Type; }
 static byte[] first;
 static byte[] salt;
 static HashSet<string> tested = new HashSet<string>();
 static int candidates;
 static byte[] Slice(byte[] data,int start,int length) { var v=new byte[length]; Buffer.BlockCopy(data,start,v,0,length); return v; }
 static byte[] MacKey(byte[] key) {
  var s=(byte[])salt.Clone(); for(int i=0;i<s.Length;i++)s[i]^=0x3a;
  using(var k=new Rfc2898DeriveBytes(key,s,2,HashAlgorithmName.SHA512)) return k.GetBytes(32);
 }
 static bool Valid(byte[] page,byte[] macKey,uint pageNo) {
  int skip=pageNo==1?16:0;
  var data=new byte[4032-skip+4]; Buffer.BlockCopy(page,skip,data,0,4032-skip);
  Buffer.BlockCopy(BitConverter.GetBytes(pageNo),0,data,4032-skip,4);
  using(var mac=new HMACSHA512(macKey)) {
   var digest=mac.ComputeHash(data); int diff=0;
   for(int i=0;i<64;i++)diff|=digest[i]^page[4032+i]; return diff==0;
  }
 }
 static byte[] TryKey(byte[] key) {
  byte[] macKey=null;bool accepted=false;
  try {
   string id;using(var hash=SHA256.Create())id=Convert.ToBase64String(hash.ComputeHash(key));
   if(!tested.Add(id))return null;
   candidates++;macKey=MacKey(key);accepted=Valid(first,macKey,1);return accepted?key:null;
  } finally {if(macKey!=null)Array.Clear(macKey,0,macKey.Length);if(!accepted)Array.Clear(key,0,key.Length);}
 }
 static int Hex(byte c) { if(c>=48&&c<=57)return c-48; if(c>=65&&c<=70)return c-55; if(c>=97&&c<=102)return c-87; return -1; }
 static byte[] Search(byte[] buf,int length) {
  for(int i=0;i<length-99;i++) {
   if(buf[i]==120&&buf[i+1]==39&&buf[i+98]==39) {
    var k=new byte[32]; bool good=true;
    for(int j=0;j<96;j++){if(Hex(buf[i+2+j])<0){good=false;break;}}
    if(good){for(int j=0;j<32;j++)k[j]=(byte)((Hex(buf[i+2+j*2])<<4)|Hex(buf[i+3+j*2])); var match=TryKey(k);if(match!=null)return match;}
   }
  }
  for(int i=0;i<=length-16;i++) {
   if(buf[i]!=salt[0])continue; bool same=true;
   for(int j=1;j<16;j++){if(buf[i+j]!=salt[j]){same=false;break;}}
   if(!same)continue;
   foreach(int delta in new int[]{-32,-40,-48,16,24,32}) {
    int start=i+delta;if(start<0||start+32>length)continue;
    var match=TryKey(Slice(buf,start,32));if(match!=null)return match;
   }
  }
  return null;
 }
 static byte[] Scan(int pid,out long bytesRead,out int regions) {
  bytesRead=0;regions=0;
  IntPtr h=OpenProcess(0x410,false,pid);
  if(h==IntPtr.Zero)throw new Exception("OpenProcess denied: "+Marshal.GetLastWin32Error());
  try {
   ulong addr=0; MBI m;
   while(VirtualQueryEx(h,new UIntPtr(addr),out m,new UIntPtr((uint)Marshal.SizeOf(typeof(MBI)))).ToUInt64()!=0) {
    ulong b=m.BaseAddress.ToUInt64(), size=m.RegionSize.ToUInt64(); uint p=m.Protect&0xff;
    if(m.State==0x1000&&(m.Protect&0x100)==0&&(p==4||p==8||p==0x40||p==0x80)) {
     regions++;
     for(ulong offset=0;offset<size;) {
      int n=(int)Math.Min((ulong)(2*1024*1024),size-offset);var buf=new byte[n];UIntPtr count;
      ReadProcessMemory(h,new UIntPtr(b+offset),buf,new UIntPtr((uint)n),out count);
      int got=(int)count.ToUInt64(); bytesRead+=got;
      if(got>0){var key=Search(buf,got);Array.Clear(buf,0,buf.Length);if(key!=null)return key;}
      offset+=(ulong)(n>128?n-128:n);
     }
    }
    ulong next=b+size; if(next<=addr)break;addr=next;
   }
  } finally {CloseHandle(h);}
  return null;
 }
 public static string Run(IntPtr handle,string source,string output) {
  tested.Clear(); candidates=0;
  byte[] key=null;
  try {
  using(var f=new FileStream(source,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete)) {
   first=new byte[4096];if(f.Read(first,0,4096)!=4096)throw new Exception("Short database");
  }
  salt=Slice(first,0,16);
  if(Encoding.ASCII.GetString(salt).StartsWith("SQLite format 3"))throw new Exception("Input already plaintext");
  long scanned;int regions; key=ScanRuntime(handle,out scanned,out regions);
  if(key==null)return "{\"key_found\":false,\"candidate_count\":"+candidates+",\"scanned_bytes\":"+scanned+",\"regions\":"+regions+",\"runtime_needles\":"+runtimeNeedles+",\"runtime_nodes\":"+runtimeNodes+",\"runtime_blobs\":"+runtimeBlobs+"}";
   return Decrypt(source,output,key,scanned,regions);
  } finally {if(key!=null)Array.Clear(key,0,key.Length);tested.Clear();if(first!=null)Array.Clear(first,0,first.Length);if(salt!=null)Array.Clear(salt,0,salt.Length);}
 }
 static string Decrypt(string source,string output,byte[] key,long scanned,int regions) {
  byte[] macKey=MacKey(key);long pages=0,zeroPages=0;bool created=false;
  try {
   using(var input=new FileStream(source,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete))
   using(var dest=new FileStream(output,FileMode.CreateNew,FileAccess.Write,FileShare.None))
   {
    created=true;
   using(var aes=Aes.Create()) {
    if(input.Length%4096!=0)throw new Exception("Unaligned database size");
    aes.Key=key;aes.Mode=CipherMode.CBC;aes.Padding=PaddingMode.None;
    var page=new byte[4096];
    while(input.Position<input.Length) {
     int offset=0;while(offset<4096){int n=input.Read(page,offset,4096-offset);if(n==0)throw new Exception("Short page");offset+=n;}
     uint number=(uint)(pages+1);
     bool zero=true;for(int zi=0;zi<page.Length;zi++)if(page[zi]!=0){zero=false;break;}
     if(zero){dest.Write(page,0,page.Length);zeroPages++;pages++;continue;}
     if(!Valid(page,macKey,number))throw new Exception("Page authentication failed at "+number);
     int skip=number==1?16:0;
     aes.IV=Slice(page,4016,16);
     byte[] plain;
     using(var dec=aes.CreateDecryptor())plain=dec.TransformFinalBlock(page,skip,4016-skip);
     var result=new byte[4096];
     if(skip==16)Buffer.BlockCopy(Encoding.ASCII.GetBytes("SQLite format 3\0"),0,result,0,16);
     Buffer.BlockCopy(plain,0,result,skip,plain.Length);
     dest.Write(result,0,result.Length);Array.Clear(plain,0,plain.Length);Array.Clear(result,0,result.Length);pages++;
    }
    dest.Flush(true);
   }
   }
  } catch {if(created&&File.Exists(output))File.Delete(output);throw;}
  finally {Array.Clear(macKey,0,macKey.Length);}
  return "{\"key_found\":true,\"all_nonzero_pages_hmac_valid\":true,\"zero_pages_preserved\":"+zeroPages+",\"pages_decrypted\":"+pages+",\"candidate_count\":"+candidates+",\"scanned_bytes\":"+scanned+",\"regions\":"+regions+"}";
 }
 public static bool SelfTest(string input,string output,byte[] key) {
  using(var f=File.OpenRead(input)){first=new byte[4096];f.Read(first,0,4096);}salt=Slice(first,0,16);
  byte[] mac=MacKey(key);bool valid;try{valid=Valid(first,mac,1);}finally{Array.Clear(mac,0,mac.Length);}
  if(!valid)return false;
  Decrypt(input,output,key,0,0);return true;
 }
}
