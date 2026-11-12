' NGAME-CM — silent scheduler start for the Windows Startup folder.
' Prefer a shortcut to this file in shell:startup (avoids a flashing console).
' This script must live next to start-scheduler.bat at the repository root.
Option Explicit
Dim sh, fso, root, bat
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
bat = root & "\start-scheduler.bat"
If Not fso.FileExists(bat) Then
  MsgBox "NGAME-CM: start-scheduler.bat not found next to start-scheduler-silent.vbs." & vbCrLf & root, vbCritical, "NGAME-CM"
  WScript.Quit 1
End If
Set sh = CreateObject("WScript.Shell")
' WindowStyle 0 = hidden; False = do not wait for the bat to finish
sh.Run """" & bat & """", 0, False
