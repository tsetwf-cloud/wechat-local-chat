// Security regressions. Synthetic files and this test's own process only.
using System;
using System.IO;
using System.Reflection;
using System.Security.AccessControl;
using System.Security.Principal;
public static class SecurityFixture {
 static void Require(bool x,string why){if(!x)throw new Exception(why);}
 public static int Main(string[] args) {
  try {
   string root=args[0];Directory.CreateDirectory(root);
   string before=Directory.GetAccessControl(root).GetSecurityDescriptorSddlForm(AccessControlSections.All);
   MethodInfo create=typeof(MainCollector).GetMethod("CreatePrivateCapture",BindingFlags.Public|BindingFlags.Static);
   Require(create!=null,"new private child API missing");
   string child=(string)create.Invoke(null,new object[]{root});
   Require(before==Directory.GetAccessControl(root).GetSecurityDescriptorSddlForm(AccessControlSections.All),"parent ACL modified");
   Require(Path.GetDirectoryName(child)==Path.GetFullPath(root),"capture not under parent");
   var acl=Directory.GetAccessControl(child);Require(acl.AreAccessRulesProtected,"child inherits public permissions");
   string sid=WindowsIdentity.GetCurrent().User.Value;
   foreach(FileSystemAccessRule r in acl.GetAccessRules(true,true,typeof(SecurityIdentifier))) {
    string who=((SecurityIdentifier)r.IdentityReference).Value;
    Require(r.AccessControlType==AccessControlType.Allow&&(who==sid||who=="S-1-5-18"),"unexpected child ACE");
   }
   Console.WriteLine("PASS private_child_preserves_parent_acl");
   MethodInfo integrity=typeof(MainCollector).GetMethod("ValidateSqlite",BindingFlags.Public|BindingFlags.Static);
   Require(integrity!=null,"mandatory SQLite integrity API missing");
   string broken=Path.Combine(child,"broken.db");File.WriteAllBytes(broken,new byte[4096]);
   bool rejected=false;try{integrity.Invoke(null,new object[]{broken});}catch(TargetInvocationException){rejected=true;}
   Require(rejected,"corrupt SQLite accepted");Console.WriteLine("PASS corrupt_sqlite_rejected");
   string existing=Path.Combine(child,"existing.db");File.WriteAllText(existing,"keep me");
   MethodInfo decrypt=typeof(WeChatDecryptProbe).GetMethod("Decrypt",BindingFlags.NonPublic|BindingFlags.Static);
   typeof(WeChatDecryptProbe).GetField("salt",BindingFlags.NonPublic|BindingFlags.Static).SetValue(null,new byte[16]);
   try{decrypt.Invoke(null,new object[]{broken,existing,new byte[32],0L,0});}catch(TargetInvocationException){}
   Require(File.ReadAllText(existing)=="keep me","existing output destroyed");Console.WriteLine("PASS preexisting_output_preserved");
   MethodInfo open=typeof(WeChatDecryptProbe).GetMethod("OpenAuthorizedProcess",BindingFlags.Public|BindingFlags.Static);
   Require(open!=null,"process boundary API missing");
   rejected=false;try{open.Invoke(null,new object[]{System.Diagnostics.Process.GetCurrentProcess().Id});}catch(TargetInvocationException){rejected=true;}
   Require(rejected,"non-Weixin process accepted");Console.WriteLine("PASS other_process_rejected");
   Console.WriteLine("RESULT security_checks=4 passed=true");return 0;
  }catch(Exception e){Console.WriteLine("FAIL "+e.GetType().Name+": "+e.Message);return 1;}
 }
}
