Option Explicit

Private Const InputRow = 101


Private Sub UploadPositions_Click()
    On Error Resume Next
    If InStr(UploadSelector.Value, "Selected") > 0 Then
        Application.Run "ItsXL.xla!UploadSelectedPositions"
    Else
        Application.Run "ItsXL.xla!UploadAllPositions"
    End If
End Sub


Private Sub DeletePositions_Click()
    On Error Resume Next
    If InStr(UploadSelector.Value, "Selected") > 0 Then
        Application.Run "ItsXL.xla!DeleteSelectedPositions"
    Else
        Application.Run "ItsXL.xla!DeleteAllPositions"
    End If
End Sub


Private Sub UploadSelector_Change()
    On Error Resume Next
    If InStr(UploadSelector.Value, "Through") > 0 Then
        TextBox1.BackColor = -2147483643
        TextBox1.Enabled = True
    Else
        TextBox1.BackColor = 12632256
        TextBox1.Enabled = False
        TextBox1.Value = ""
    End If
End Sub


Private Sub AddInput_Click()
    Randomize
    Dim newInputName As String
    newInputName = "ComboBoxCustom" & "_" & Round(Rnd() * 1000000)
    
    'add a new column
    Dim col As Integer
    col = Me.Range("Its_zNextColumn").Column
    Me.Columns(col).Insert
    
    'add a new input ComboBox
    Dim newInputLinkedCell As Range
    Set newInputLinkedCell = Me.Cells(InputRow, col)
    Me.Range(ComboBox8.LinkedCell).Copy
    newInputLinkedCell.PasteSpecial Paste:=xlFormats
    
    ComboBox8.Copy
    newInputLinkedCell.Select
    Me.Paste
    
    With Me.OLEObjects(getNewComboBoxName())
        .LinkedCell = newInputLinkedCell.Address
        .Name = newInputName
    End With
    
    'add callback for the new input
    Dim iRow As Integer
    With Me.Parent.VBProject.VBComponents(Me.CodeName).CodeModule
        iRow = .CountOfLines
        Call .InsertLines(iRow + 1, "Private Sub " & newInputName & "_Change()")
        Call .InsertLines(iRow + 2, "    On Error Resume Next")
        Call .InsertLines(iRow + 3, "    Call handleChange(" & newInputName & ".Value, Range(" & newInputName & ".LinkedCell))")
        Call .InsertLines(iRow + 4, "End Sub")
    End With

    Me.Range("Its_zNextColumn").Select
End Sub

Private Sub RemoveInput_Click()
    On Error Resume Next
    
    Dim remInputLinkedCell As Range
    Set remInputLinkedCell = Cells(InputRow, Application.Selection.Column)
    
    Dim obj As OLEObject
    For Each obj In Me.OLEObjects
        If InStr(obj.Name, "ComboBox") > 0 Then
            If Range(obj.LinkedCell).Address <> remInputLinkedCell.Address Then
                'if above condition throws we'll get here
            Else
                If InStr(obj.Name, "Custom") > 0 Then
                    Me.Names(getAppHandle(remInputLinkedCell.Value)).Delete
                    Me.Columns(remInputLinkedCell.Column).Delete
                    
                    With Me.Parent.VBProject.VBComponents(Me.CodeName).CodeModule
                        Call .DeleteLines(.ProcStartLine(obj.Name & "_Change", 0), 4)
                    End With
                    obj.Delete
                    
                Else
                    MsgBox "This input column can not be removed. Please, select a different one.", vbExclamation
                End If
                
                Exit For
            End If
        End If
    Next obj
    
    If obj Is Nothing Then
        MsgBox "Please, select an input column to remove.", vbExclamation
    End If
End Sub


Private Sub ComboBox1_Change()
    On Error Resume Next
    Call handleChange(ComboBox1.Value, Range(ComboBox1.LinkedCell))
End Sub


Private Sub ComboBox2_Change()
    On Error Resume Next
    Call handleChange(ComboBox2.Value, Range(ComboBox2.LinkedCell))
End Sub


Private Sub ComboBox3_Change()
    On Error Resume Next
    Call handleChange(ComboBox3.Value, Range(ComboBox3.LinkedCell))
End Sub


Private Sub ComboBox4_Change()
    On Error Resume Next
    Call handleChange(ComboBox4.Value, Range(ComboBox4.LinkedCell))
End Sub


Private Sub ComboBox5_Change()
    On Error Resume Next
    Call handleChange(ComboBox5.Value, Range(ComboBox5.LinkedCell))
End Sub


Private Sub ComboBox6_Change()
    On Error Resume Next
    Call handleChange(ComboBox6.Value, Range(ComboBox6.LinkedCell))
End Sub


Private Sub ComboBox7_Change()
    On Error Resume Next
    Call handleChange(ComboBox7.Value, Range(ComboBox7.LinkedCell))
End Sub


Private Sub ComboBox8_Change()
    On Error Resume Next
    Call handleChange(ComboBox8.Value, Range(ComboBox8.LinkedCell))
End Sub


Private Sub handleChange(inputName As String, location As Range)
    On Error Resume Next
    
    Dim oName As Excel.Name
    For Each oName In Me.Names
        If InStr(oName.RefersTo, "REF") > 0 Then
            Call oName.Delete
        ElseIf oName.RefersToRange.Address = location.Address Then
            Call oName.Delete
        End If
    Next oName

    Dim appHandle As String
    appHandle = getAppHandle(inputName)
    
    If Me.Names(appHandle) Is Nothing Then
        Call Me.Names.Add(appHandle, location, True)
    Else
        MsgBox "Input is already defined. Please choose a different one.", vbExclamation
        location.Value = ""
    End If
End Sub


Private Function getAppHandle(inputName As String) As String
    If Not inputName = "" Then
        getAppHandle = "Its_" & Trim(WorksheetFunction.Index(Me.Range("Its_zAppHandle"), WorksheetFunction.Match(inputName, Me.Range("Its_zPrompt"), 0), 1, 1)) & "_I"
    End If
End Function


Private Function getNewComboBoxName() As String
    On Error Resume Next

    Dim maxComboBoxId As Long
    maxComboBoxId = 0

    Dim comboBoxBaseName As String
    comboBoxBaseName = "ComboBox"

    Dim comboBoxBaseNameLen As Long
    comboBoxBaseNameLen = Len(comboBoxBaseName)

    Dim o As OLEObject
    Dim id As Long
    For Each o In Me.OLEObjects
        If InStr(o.Name, comboBoxBaseName) > 0 Then
            id = CLng(Right(o.Name, Len(o.Name) - comboBoxBaseNameLen))
            
            If maxComboBoxId < id Then
                maxComboBoxId = id
            End If
        End If
    Next o

    getNewComboBoxName = comboBoxBaseName & maxComboBoxId

End Function
