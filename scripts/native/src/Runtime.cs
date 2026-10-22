// Runtime Config.Cipher layout adapted from MIT wcdb-key-tool commit
// 79f1b5b92e12c66aa281b4a60a3c478b5f547dfa. No debugger attachment or writes.
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static partial class WeChatDecryptProbe {
 static int runtimeNeedles,runtimeNodes,runtimeBlobs;
 static byte[] ReadMem(IntPtr h,ulong address,int n) {
  var data=new byte[n];UIntPtr got;ReadProcessMemory(h,new UIntPtr(address),data,new UIntPtr((uint)n),out got);
  if(got.ToUInt64()==(ulong)n)return data;Array.Clear(data,0,data.Length);return null;
 }
 static ulong U64(byte[] x,int i){return x!=null&&i+8<=x.Length?BitConverter.ToUInt64(x,i):0;}
 static bool Ptr(ulong x){return x>=0x10000&&x<0x800000000000;}
 static List<ulong[]> ReadableRegions(IntPtr h) {
  var regions=new List<ulong[]>();ulong addr=0;MBI m;
  while(VirtualQueryEx(h,new UIntPtr(addr),out m,new UIntPtr((uint)Marshal.SizeOf(typeof(MBI)))).ToUInt64()!=0) {
   ulong b=m.BaseAddress.ToUInt64(),size=m.RegionSize.ToUInt64();uint p=m.Protect&0xff;
   if(m.State==0x1000&&(m.Protect&0x100)==0&&(p==2||p==4||p==8||p==0x20||p==0x40||p==0x80))regions.Add(new ulong[]{b,size});
   ulong next=b+size;if(next<=addr)break;addr=next;
  }
  return regions;
 }
 static bool At(byte[] x,int i,byte[] needle){if(i+needle.Length>x.Length)return false;for(int j=0;j<needle.Length;j++)if(x[i+j]!=needle[j])return false;return true;}
 static byte[] DecodeBlob(byte[] blob) {
  try {
  byte[] mask=new byte[]{0xd2,0xc7,0x44,0x24,0x58,0x02,0,0,0,0x48,0x89,0x44,0x24,0x50,0x48,0x8b,0x45,0,0x48,0x84,0x4c,0x24,0x48,0x48,0x89,0x44,0x25,0x40,0x48,0x58,0x4c,0x24};
  for(int i=0;i<blob.Length;i++)blob[i]^=mask[i%mask.Length];
  for(int i=0;i+66<blob.Length;i++) {
   if((blob[i]!=120&&blob[i]!=88)||blob[i+1]!=39)continue;
   int end=i+2;while(end<blob.Length&&Hex(blob[end])>=0)end++;
   int count=end-i-2;if(end>=blob.Length||blob[end]!=39||count<64||count>192)continue;
   var starts=new List<int>();starts.Add(0);if(count>96){for(int s=0;s+64<=count;s+=32)starts.Add(s);starts.Add(count-64);}
   foreach(int start in starts){var k=new byte[32];for(int j=0;j<32;j++)k[j]=(byte)((Hex(blob[i+2+start+j*2])<<4)|Hex(blob[i+3+start+j*2]));var key=TryKey(k);if(key!=null){Array.Clear(blob,0,blob.Length);return key;}}
  }
  return null;
  } finally {Array.Clear(blob,0,blob.Length);}
 }
 static byte[] ScanRuntime(IntPtr h,out long bytesRead,out int regionCount) {
  bytesRead=0;regionCount=0;runtimeNeedles=runtimeNodes=runtimeBlobs=0;

   var regions=ReadableRegions(h);regionCount=regions.Count;
   byte[] needle=Encoding.ASCII.GetBytes("com.Tencent.WCDB.Config.Cipher");var addresses=new HashSet<ulong>();
   foreach(var r in regions)for(ulong offset=0;offset<r[1];) {
    int n=(int)Math.Min((ulong)(2*1024*1024),r[1]-offset);var data=ReadMem(h,r[0]+offset,n);
    if(data!=null){bytesRead+=n;for(int i=0;i+needle.Length<=n;i++)if(data[i]==needle[0]&&At(data,i,needle))addresses.Add(r[0]+offset+(ulong)i);Array.Clear(data,0,data.Length);}
    offset+=(ulong)(n>128?n-128:n);
   }
   runtimeNeedles=addresses.Count;if(addresses.Count==0)return null;
   var seen=new HashSet<ulong>();
   foreach(var r in regions)for(ulong offset=0;offset<r[1];) {
    int n=(int)Math.Min((ulong)(2*1024*1024),r[1]-offset);var data=ReadMem(h,r[0]+offset,n);
    if(data!=null) {
     try {
     bytesRead+=n;
     for(int i=0;i+16<=n;i+=8) {
      if(U64(data,i+8)!=(ulong)needle.Length||!addresses.Contains(U64(data,i)))continue;
      ulong q=r[0]+offset+(ulong)i;if(q<16)continue;
      var node=ReadMem(h,q-16,0x50);ulong ptr=U64(node,0x28);if(!Ptr(ptr)||!seen.Add(ptr))continue;runtimeNodes++;
      var obj=ReadMem(h,ptr+0x88,0x28);ulong bp=U64(obj,8),len=U64(obj,16);if(!Ptr(bp)||len==0||len>1024)continue;
      var blob=ReadMem(h,bp,(int)len);if(blob==null)continue;runtimeBlobs++;
      var key=DecodeBlob(blob);if(key!=null){Array.Clear(data,0,data.Length);return key;}
     }
     } finally {Array.Clear(data,0,data.Length);}
    }
    offset+=(ulong)(n>128?n-128:n);
   }

  return null;
 }
}
