Sub Consolidation()
    Dim i As Integer
    Dim curRow As Integer
    Dim constitRange As Variant
    Dim largeRange As Variant
    Dim midRange As Variant
    Dim smallRange As Variant
    Dim outRange As Variant
    Dim ratio As Variant
    Dim dict As Variant
    
    Set ratio = CreateObject("Scripting.Dictionary")
    Set dict = CreateObject("Scripting.Dictionary")
    
    Sheets("Ratio").Activate
    Set inRange = ActiveSheet.Range("a2", ActiveSheet.Range("a2").End(xlDown).End(xlToRight))
    For i = 1 To inRange.Rows.Count
        ratio.Add inRange(i, 1).Value, inRange(i, 2).Value
    Next
    
    Sheets("HSI Constituent").Activate
    Set constitRange = ActiveSheet.Range("a2", ActiveSheet.Range("a2").End(xlDown).End(xlToRight))
    
    Sheets("HSI LargeCap").Activate
    Set largeRange = ActiveSheet.Range("a2", ActiveSheet.Range("a2").End(xlDown).End(xlToRight))
    
    Sheets("HSI MidCap").Activate
    Set midRange = ActiveSheet.Range("a2", ActiveSheet.Range("a2").End(xlDown).End(xlToRight))
    
    Sheets("HSI SmallCap").Activate
    Set smallRange = ActiveSheet.Range("a2", ActiveSheet.Range("a2").End(xlDown).End(xlToRight))
    
    'Set outRange = Application.Union(constitRange, largeRange, midRange, smallRange)
    
    curRow = 1
    Sheets("All").Activate
    Cells.Clear
    
    Cells(curRow, 1) = "Code"
    Cells(curRow, 2) = "Stock Name"
    Cells(curRow, 3) = "Category"
    Cells(curRow, 4) = "Ratio"
    curRow = curRow + 1
    
    For i = 1 To constitRange.Rows.Count
        If Not dict.Exists(constitRange(i, 1) & ";" & constitRange(i, 2)) Then
            dict.Add largeRange(i, 1) & ";" & largeRange(i, 2), "HSI LargeCap" & ";" & ratio("HSI LargeCap")
        End If
    Next
    
    For i = 1 To largeRange.Rows.Count
        If Not dict.Exists(largeRange(i, 1) & ";" & largeRange(i, 2)) Then
            dict.Add largeRange(i, 1) & ";" & largeRange(i, 2), "HSI LargeCap" & ";" & ratio("HSI LargeCap")
        End If
    Next
    
    For i = 1 To midRange.Rows.Count
        If Not dict.Exists(midRange(i, 1) & ";" & midRange(i, 2)) Then
            dict.Add midRange(i, 1) & ";" & midRange(i, 2), "HSI MidCap" & ";" & ratio("HSI MidCap")
        End If
    Next
    
    For i = 0 To dict.Count - 1
        Dim keyArr As Variant
        Dim itmArr As Variant
        
        keyArr = Split(dict.Keys()(i), ";")
        itmArr = Split(dict.Items()(i), ";")
        
        Cells(curRow + i, 1) = keyArr(0)
        Cells(curRow + i, 2) = keyArr(1)
        Cells(curRow + i, 3) = itmArr(0)
        Cells(curRow + i, 4) = itmArr(1)
    Next
End Sub
