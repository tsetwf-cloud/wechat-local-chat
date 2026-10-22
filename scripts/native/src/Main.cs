using System;
using System.IO;
using System.Diagnostics;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Security.Cryptography;
using System.Runtime.InteropServices;

// Main-database-only acquisition. No WAL reads and no source writes.
public static class MainCollector {
 [DllImport("winsqlite3.dll",CallingConvention=CallingConvention.Cdecl)] static extern int sqlite3_open_v2(byte[] name,out IntPtr db,int flags,IntPtr vfs);
 [DllImport("winsqlite3.dll",CallingConvention=CallingConvention.Cdecl)] static extern int sqlite3_prepare_v2(IntPtr db,byte[] sql,int n,out IntPtr stmt,IntPtr tail);
 [DllImport("winsqlite3.dll",CallingConvention=CallingConvention.Cdecl)] static extern int sqlite3_step(IntPtr stmt);
 [DllImport("winsqlite3.dll",CallingConvention=CallingConvention.Cdecl)] static extern IntPtr sqlite3_column_text(IntPtr stmt,int i);
 [DllImport("winsqlite3.dll",CallingConvention=CallingConvention.Cdecl)] static extern int sqlite3_finalize(IntPtr stmt);
 [DllImport("winsqlite3.dll",CallingConvention=CallingConvention.Cdecl)] static extern int sqlite3_close(IntPtr db);
 static byte[] Utf8(string s){return System.Text.Encoding.UTF8.GetBytes(s+"\0");}
 public static void ValidateSqlite(string path) {
  IntPtr db=IntPtr.Zero,stmt=IntPtr.Zero;
  try {
   string uri=new Uri(Path.GetFullPath(path)).AbsoluteUri+"?mode=ro&immutable=1";
   if(sqlite3_open_v2(Utf8(uri),out db,0x41,IntPtr.Zero)!=0)throw new Exception("SQLite open failed");
   if(sqlite3_prepare_v2(db,Utf8("PRAGMA integrity_check"),-1,out stmt,IntPtr.Zero)!=0)throw new Exception("SQLite prepare failed");
   if(sqlite3_step(stmt)!=100||Marshal.PtrToStringAnsi(sqlite3_column_text(stmt,0))!="ok"||sqlite3_step(stmt)!=101)throw new Exception("SQLite integrity failed");
  } finally {if(stmt!=IntPtr.Zero)sqlite3_finalize(stmt);if(db!=IntPtr.Zero)sqlite3_close(db);}
 }
 public static string CreatePrivateCapture(string parent) {
  parent=Path.GetFullPath(parent);
  if(!Directory.Exists(parent))throw new Exception("Output parent must already exist");
  for(var d=new DirectoryInfo(parent);d!=null;d=d.Parent)
   if((d.Attributes&FileAttributes.ReparsePoint)!=0)throw new Exception("Reparse-point parent rejected");
  var sid=WindowsIdentity.GetCurrent().User;
  var acl=new DirectorySecurity();acl.SetOwner(sid);acl.SetAccessRuleProtection(true,false);
  foreach(var who in new SecurityIdentifier[]{sid,new SecurityIdentifier("S-1-5-18")})
   acl.AddAccessRule(new FileSystemAccessRule(who,FileSystemRights.FullControl,InheritanceFlags.ContainerInherit|InheritanceFlags.ObjectInherit,PropagationFlags.None,AccessControlType.Allow));
  string child=Path.Combine(parent,Guid.NewGuid().ToString("N"));
  new DirectoryInfo(child).Create(acl);
  var actual=Directory.GetAccessControl(child);
  if(!actual.AreAccessRulesProtected||!actual.GetOwner(typeof(SecurityIdentifier)).Equals(sid))throw new Exception("Private ACL verification failed");
  int rules=0;
  foreach(FileSystemAccessRule r in actual.GetAccessRules(true,true,typeof(SecurityIdentifier))) {
   string who=((SecurityIdentifier)r.IdentityReference).Value;
   if(r.AccessControlType!=AccessControlType.Allow||(who!=sid.Value&&who!="S-1-5-18")||r.FileSystemRights!=FileSystemRights.FullControl)throw new Exception("Unexpected output ACL");
   rules++;
  }
  if(rules!=2)throw new Exception("Incomplete private ACL");return child;
 }
 static string Hash(string path) {
  using(var f=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete))
  using(var h=SHA256.Create())return Convert.ToBase64String(h.ComputeHash(f));
 }
 static string Q(string s) {
  var b=new System.Text.StringBuilder("\"");
  foreach(char c in s) {
   if(c=='\\'||c=='\"')b.Append('\\').Append(c);
   else if(c<32)b.Append("\\u").Append(((int)c).ToString("x4"));
   else b.Append(c);
  }
  return b.Append('"').ToString();
 }
 public static void CaptureMain(string source,string target) {
  string before=Hash(source);
  using(var input=new FileStream(source,FileMode.Open,FileAccess.Read,FileShare.ReadWrite|FileShare.Delete))
  using(var output=new FileStream(target,FileMode.CreateNew,FileAccess.Write,FileShare.None)) {
   input.CopyTo(output);output.Flush(true);
  }
  if(before!=Hash(source)||before!=Hash(target))throw new Exception("Database changed during capture; retry required");
 }
 public static int Main(string[] args) {
  string stage="arguments";
  try {
   if(args.Length!=3){Console.WriteLine("usage: probe_main PID SOURCE_DB PRIVATE_OUTPUT_ROOT");return 2;}
   int pid=int.Parse(args[0]);string source=Path.GetFullPath(args[1]),root=Path.GetFullPath(args[2]);
   if(!File.Exists(source)||!source.EndsWith(".db",StringComparison.OrdinalIgnoreCase))throw new Exception("An existing .db input is required");
   // Restrict ACLs only inside a dedicated output tree, never the source tree.
   if(source.StartsWith(root.TrimEnd('\\')+"\\",StringComparison.OrdinalIgnoreCase))throw new Exception("Output root must not contain the source database");
   stage="authorize_process";
   using(var processHandle=WeChatDecryptProbe.OpenAuthorizedProcess(pid)) {
   string version=WeChatDecryptProbe.ValidatedVersion(processHandle.DangerousGetHandle());
   stage="private_directory";string dir=CreatePrivateCapture(root);
   string encrypted=Path.Combine(dir,"encrypted.db"),decrypted=Path.Combine(dir,"decrypted.db");
   stage="copy_main_database";CaptureMain(source,encrypted);
   var timer=Stopwatch.StartNew();
   stage="read_process_and_decrypt";string result=WeChatDecryptProbe.Run(processHandle.DangerousGetHandle(),encrypted,decrypted);timer.Stop();
   if(!File.Exists(decrypted))return 3;
   stage="sqlite_integrity";ValidateSqlite(decrypted);
   result=result.Substring(0,result.Length-1)+",\"sqlite_integrity_ok\":true}";
   Console.WriteLine("{\"wechat_version\":"+Q(version)+",\"pid\":"+pid+",\"source_name\":"+Q(Path.GetFileName(source))+",\"source_copy_hash_stable\":true,\"capture_mode\":\"main-db-only\",\"wal_included\":false,\"completeness_warning\":\"Recent committed messages still in WAL are excluded\",\"original_modified\":false,\"decrypted_path\":"+Q(decrypted)+",\"elapsed_ms\":"+timer.ElapsedMilliseconds+",\"result\":"+result+"}");
   return 0;
   }
  } catch(Exception e) {
   // Do not print arbitrary exception messages that may contain private paths.
   string reason=e.Message.Contains("changed during capture")?"Database changed during capture; retry required":"See stage and error type; no key or database body is logged";
   Console.WriteLine("{\"error\":true,\"stage\":"+Q(stage)+",\"type\":"+Q(e.GetType().Name)+",\"reason\":"+Q(reason)+"}");return 1;
  }
 }
}
