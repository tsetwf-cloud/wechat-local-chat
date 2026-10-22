// Synthetic crypto fixtures only. Never scans a process or reads user databases.
using System;
using System.IO;
using System.Text;
using System.Security.Cryptography;
public static class MainFixture {
 static byte[] key=new byte[32],salt=new byte[16];
 static void Require(bool x,string why){if(!x)throw new Exception(why);}
 static byte[] Page(uint number) {
  byte[] page=new byte[4096],iv=new byte[16],plain=new byte[4016],s=(byte[])salt.Clone();
  for(int i=0;i<plain.Length;i++)plain[i]=(byte)(i%199);
  for(int i=0;i<16;i++){iv[i]=(byte)(i+3);s[i]^=0x3a;}
  int skip=number==1?16:0;
  if(skip!=0)Buffer.BlockCopy(salt,0,page,0,16);
  using(var aes=Aes.Create()) {
   aes.Key=key;aes.IV=iv;aes.Mode=CipherMode.CBC;aes.Padding=PaddingMode.None;
   using(var enc=aes.CreateEncryptor()) {
    var c=enc.TransformFinalBlock(plain,skip,4016-skip);Buffer.BlockCopy(c,0,page,skip,c.Length);
   }
  }
  Buffer.BlockCopy(iv,0,page,4016,16);
  byte[] signed=new byte[4032-skip+4];Buffer.BlockCopy(page,skip,signed,0,4032-skip);
  Buffer.BlockCopy(BitConverter.GetBytes(number),0,signed,4032-skip,4);
  using(var deriv=new Rfc2898DeriveBytes(key,s,2,HashAlgorithmName.SHA512))
  using(var mac=new HMACSHA512(deriv.GetBytes(32)))Buffer.BlockCopy(mac.ComputeHash(signed),0,page,4032,64);
  return page;
 }
 public static int Main(string[] args) {
  try {
   string root=args[0];Directory.CreateDirectory(root);
   for(int i=0;i<32;i++)key[i]=(byte)(i+1);
   for(int i=0;i<16;i++)salt[i]=(byte)(i+96);
   string source=Path.Combine(root,"fixture.db"),output=Path.Combine(root,"plain.db");
   byte[] data=new byte[12288];Buffer.BlockCopy(Page(1),0,data,0,4096);Buffer.BlockCopy(Page(2),0,data,4096,4096);
   File.WriteAllBytes(source,data);File.WriteAllText(source+"-wal","malformed WAL must be ignored");
   Require(WeChatDecryptProbe.SelfTest(source,output,key),"valid key rejected");
   byte[] result=File.ReadAllBytes(output);Require(result.Length==data.Length,"size mismatch");
   Require(Encoding.ASCII.GetString(result,0,16)=="SQLite format 3\0","header mismatch");
   for(int i=16;i<4016;i++)Require(result[i]==(byte)(i%199),"page1 mismatch");
   for(int i=0;i<4016;i++)Require(result[4096+i]==(byte)(i%199),"page2 mismatch");
   for(int i=8192;i<12288;i++)Require(result[i]==0,"zero page changed");
   byte[] wrong=(byte[])key.Clone();wrong[0]^=1;
   Require(!WeChatDecryptProbe.SelfTest(source,Path.Combine(root,"wrong.db"),wrong),"wrong key accepted");
   data[4100]^=1;File.WriteAllBytes(source,data);
   string failed=Path.Combine(root,"failed.db");bool rejected=false;
   try{WeChatDecryptProbe.SelfTest(source,failed,key);}catch{rejected=true;}
   Require(rejected&&!File.Exists(failed),"tampered page accepted or output retained");
   string copy=Path.Combine(root,"copy.db");MainCollector.CaptureMain(source,copy);
   Require(new FileInfo(copy).Length==data.Length&&!File.Exists(copy+"-wal"),"main capture copied WAL");
   Console.WriteLine("{\"fixture_checks\":6,\"passed\":true,\"real_data_used\":false}");return 0;
  }catch(Exception e){Console.WriteLine("FAIL "+e.Message);return 1;}
 }
}
