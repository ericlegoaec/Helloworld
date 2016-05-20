'LAST UPDATE DATE:  03/04/2011
'LAST UPDATER:      Xavier Berard
Option Explicit


Private Const BLPREQUEST_ID_NON_INITIALIZED = -999999999

Private WithEvents m_Session As blpapicomLib2.Session
Private m_SessionOptions As blpapicomLib2.SessionOptions

Private m_RefDataService As blpapicomLib2.service           '//blp/refdata
Private m_SearchService As blpapicomLib2.service            '//blp/exrsvc
Private m_TADataService As blpapicomLib2.service            '//blp/tasvc
Private m_FieldInfoService As blpapicomLib2.service         '//blp/apiflds
Private m_FXAPIService As blpapicomLib2.service             '//blp/fxapisvc
Private m_InstrumentService As blpapicomLib2.service        '//blp/instruments
Private m_AuthorizationService As blpapicomLib2.service     '//blp/apiauth
Private m_MktDataService As blpapicomLib2.service           '//blp/mktdata, //blp/mktdepthdata
Private m_RunzService As blpapicomLib2.service              '//blp/runs"
Private m_MktListService As blpapicomLib2.service           '//blp/mktlist"
Private m_CurrentService As blpapicomLib2.service

Private m_Identity As blpapicomLib2.Identity
Private m_FXAPISubscriptions As blpapicomLib2.SubscriptionList
Private m_MktDataSubscriptions As blpapicomLib2.SubscriptionList

Private m_Requests As Collection
Private m_FXAPISubscriptionProcedure As String
Private m_SubscriptionProcedure As String
Private m_DataProcedure As String
Private m_StatusProcedure As String
Private m_ProgressProcedure As String
Private m_Initialized As Boolean
Private m_count As Long
Private m_EventsExpected  As Long
Private m_EventsReceived  As Long
Private m_KeepData As Boolean
Private m_LateBindding As Boolean
Private m_TimeOutMilliseconds As Long
Private m_DoEvents As Boolean
Private m_FakeEventCID As String
Private m_SessionState As String
Private m_SaveDataLog As Boolean

#If Win64 Then
    Private Declare PtrSafe Function BlpCoCreateInstance Lib "bbloaderv3.dll" (ByVal lpszFilePathName As String, ByRef rclsid As guid, riid As guid) As Object
    Private Declare PtrSafe Function CLSIDFromString Lib "ole32.dll" (pstCLS As LongPtr, clsid As guid) As Long
    Private Declare PtrSafe Function GetActiveObject Lib "Oleaut32.dll" (lpRclsid As Long, pvReserved As Long, lpUnk As Long) As Long
#Else
    Private Declare Function BlpCoCreateInstance Lib "bbloaderv3.dll" (ByVal lpszFilePathName As String, ByRef rclsid As guid, riid As guid) As Object
    Private Declare Function CLSIDFromString Lib "ole32.dll" (pstCLS As Long, clsid As guid) As Long
    Private Declare Function GetActiveObject Lib "Oleaut32.dll" (lpRclsid As Long, pvReserved As Long, lpUnk As Long) As Long
#End If

Private Type guid
    Data1 As Long
    Data2 As Integer
    Data3 As Integer
    Data4(7) As Byte
End Type

Public Event Status(ByRef strMessage As String)
Public Event Progress(ByRef dblProgress As Double, ByRef boolComplete As Boolean)
Public Event Data(ByRef objBlpReq As clsBlpRequest)
Public Event FXAPISubscription(ByRef objDic As Scripting.Dictionary)
Public Event SubscriptionData(ByRef objBlpReq As clsBlpRequest)

Private Function GuidFromStGuid(ByVal stGuid As String) As guid
    Dim rc As Long
    If Left$(stGuid, 7) = "{guid {" Then
        If Right$(stGuid, 2) = "}}" Then
            stGuid = Mid$(stGuid, 7, 38)
        End If
    End If
    rc = CLSIDFromString(ByVal StrPtr(stGuid), GuidFromStGuid)
End Function

Private Sub Class_Initialize()
    
    '
        
End Sub

Public Function Construct(Optional ByRef strServerHost As String, _
                          Optional ByRef lngServerPort As Long = -1, _
                          Optional ByRef strAuthMode As String, _
                          Optional ByRef strDirSvcName As String, _
                          Optional ByRef strAppName As String, _
                          Optional ByRef boolResetSession As Boolean) As Boolean

    m_TimeOutMilliseconds = 300000
    m_Initialized = IniSession(strServerHost, lngServerPort, strAuthMode, strDirSvcName, strAppName, boolResetSession)
    If m_Initialized Then
        Set m_Requests = New Collection
    End If
    
    Construct = m_Initialized
    
End Function

Private Sub Class_Terminate()
    Set m_Requests = Nothing
    Set m_RefDataService = Nothing
    Set m_FieldInfoService = Nothing
    Set m_Session = Nothing
End Sub

Public Property Get SessionState() As String
    SessionState = m_SessionState
End Property

Public Property Get DoEventsDuringQueue() As Boolean
    DoEventsDuringQueue = m_DoEvents
End Property

Public Property Let DoEventsDuringQueue(ByRef boolDoEvents As Boolean)
    m_DoEvents = boolDoEvents
End Property

Public Property Get SaveDataLog() As Boolean
    SaveDataLog = m_SaveDataLog
End Property

Public Property Let SaveDataLog(ByRef boolSaveDataLog As Boolean)
    m_SaveDataLog = boolSaveDataLog
End Property

Public Property Get Initialized() As Boolean
    Initialized = m_Initialized
End Property

Public Property Get TimeOutMilliseconds() As Long
    TimeOutMilliseconds = m_TimeOutMilliseconds
End Property

Public Property Let TimeOutMilliseconds(ByRef lngTimeOutMilliseconds As Long)
    m_TimeOutMilliseconds = lngTimeOutMilliseconds
End Property

Public Property Get FXAPISubscriptionProcedure() As String
    FXAPISubscriptionProcedure = m_FXAPISubscriptionProcedure
End Property

Public Property Let FXAPISubscriptionProcedure(ByRef strFXAPISubscriptionProcedure As String)
    m_FXAPISubscriptionProcedure = strFXAPISubscriptionProcedure
End Property

Public Property Get SubscriptionProcedure() As String
    SubscriptionProcedure = m_SubscriptionProcedure
End Property

Public Property Let SubscriptionProcedure(ByRef strSubscriptionProcedure As String)
    m_SubscriptionProcedure = strSubscriptionProcedure
End Property

Public Property Get DataProcedure() As String
    DataProcedure = m_DataProcedure
End Property

Public Property Let DataProcedure(ByRef strDataProcedure As String)
    m_DataProcedure = strDataProcedure
End Property

Public Property Get StatusProcedure() As String
    StatusProcedure = m_StatusProcedure
End Property

Public Property Let StatusProcedure(ByRef strStatusProcedure As String)
    m_StatusProcedure = strStatusProcedure
End Property

Public Property Get ProgressProcedure() As String
    ProgressProcedure = m_ProgressProcedure
End Property

Public Property Let ProgressProcedure(ByRef strProgressProcedure As String)
    m_ProgressProcedure = strProgressProcedure
End Property

Public Property Get Progress() As Double
    If m_EventsExpected <> 0 Then
        Progress = m_EventsReceived / m_EventsExpected
    End If
End Property

Public Property Get EventsExpected() As Long
    EventsExpected = m_EventsExpected
End Property

Public Property Get EventsReceived() As Long
    EventsReceived = m_EventsReceived
End Property

Public Property Get KeepData() As Boolean
    KeepData = m_KeepData
End Property

Public Property Let KeepData(ByRef boolKeepData As Boolean)
    m_KeepData = boolKeepData
End Property

Public Property Get Requests() As Collection
    Set Requests = m_Requests
End Property

Public Sub ResetRequests()
    Do Until m_Requests.count = 0
        Call m_Requests.Remove(1)
    Loop
    m_EventsExpected = 0
    m_EventsReceived = 0
End Sub

Public Function IniSession(Optional ByRef strServerHost As String, _
                           Optional ByRef lngServerPort As Long = -1, _
                           Optional ByRef strAuthMode As String, _
                           Optional ByRef strDirSvcName As String, _
                           Optional ByRef strAppName As String, _
                           Optional ByRef boolResetSession As Boolean) As Boolean
    
    Dim b As Boolean
    Dim strFileName As String, strAuthOptions As String
    
    If boolResetSession Then
        Call Class_Terminate
    End If

    If m_Session Is Nothing Then
    
        strFileName = "blpapicom2.dll"
        
        On Error Resume Next
        
        #If EnableDebugMode Then
            Set m_Session = New blpapicomLib2.Session
            If m_Session Is Nothing Then
                Set m_Session = BlpCoCreateInstance(strFileName, _
                    GuidFromStGuid("{guid {9FDBE237-38A5-4d8c-BB9C-2EB55FB1EABE}}"), _
                    GuidFromStGuid("{guid {4AC751C2-BB10-4702-BB05-791D93BB461C}}"))
            End If
        #Else
            Set m_Session = BlpCoCreateInstance(strFileName, _
                            GuidFromStGuid("{guid {9FDBE237-38A5-4d8c-BB9C-2EB55FB1EABE}}"), _
                            GuidFromStGuid("{guid {4AC751C2-BB10-4702-BB05-791D93BB461C}}"))
                                 
            If m_Session Is Nothing Then
                Set m_Session = New blpapicomLib2.Session
            End If
        
        #End If
    End If
    
    If Not (m_Session Is Nothing) Then
    
        Set m_SessionOptions = m_Session.CreateSessionOptions
        
        If Trim(strServerHost) <> "" Then
            m_SessionOptions.ServerHost = Trim(strServerHost)
        End If
        
        If lngServerPort <> -1 Then
            m_SessionOptions.ServerPort = lngServerPort
        End If
        
        If strServerHost <> "localhost" Then
        
            Select Case strAuthMode
                
                Case "OS_LOGON"
                    strAuthOptions = "AuthenticationType=OS_LOGON"
                
                Case "DIRECTORY_SERVICE"
                    strAuthOptions = "AuthenticationType=DIRECTORY_SERVICE;DirSvcPropertyName=" & strDirSvcName
                    
                Case "USER_AND_APPLICATION"
                    strAuthOptions = "AuthenticationMode=USER_AND_APPLICATION;ApplicationAuthenticationType=APPNAME_AND_KEY;ApplicationName=" & strAppName & ";AuthenticationType = OS_LOGON"
                
                Case "APPLICATION_ONLY"
                    strAuthOptions = "AuthenticationMode=APPLICATION_ONLY;ApplicationAuthenticationType=APPNAME_AND_KEY;ApplicationName=" & strAppName
    
            End Select
        
        End If
        
        If Trim(strAuthOptions) <> "" Then
            Call m_SessionOptions.SetAuthenticationOptions(Trim(strAuthOptions))
        End If
        
        Call m_Session.SetSessionOptions(m_SessionOptions)
    
        m_SessionState = ""
        m_Session.QueueEvents = True
        Call m_Session.start
        IniSession = True
    End If
    
    On Error GoTo 0


End Function

Private Function IniService(ByRef objService As blpapicomLib2.service, ByRef strService As String, ByRef objBlpReq As clsBlpRequest) As Boolean
    
    Dim b As Boolean
    
    If m_SessionState = "SessionTerminated" Then
        Call IniSession
    End If
    
    Call WaitForSessionStatus
    
    If m_SessionState = "SessionStarted" Then
        If objService Is Nothing Then
            If Initialized Then
                On Error Resume Next
                Call m_Session.OpenService(strService)
                '2012-07-24: This could fail if the user is not logged in
                Set objService = m_Session.GetService(strService)
                On Error GoTo 0
                If Not (objService Is Nothing) Then
                    b = True
                Else
                    If (objBlpReq Is Nothing) Then Set objBlpReq = New clsBlpRequest
                    objBlpReq.Error = "Could not open " & strService & " !"
                End If
            Else
                If (objBlpReq Is Nothing) Then Set objBlpReq = New clsBlpRequest
                objBlpReq.Error = "Could not start a v3 API Session!"
            End If
        Else
            b = True
        End If
        If b Then
            Set m_CurrentService = objService
        End If
    Else
        Call ProcessStatusEvent(m_SessionState)
    End If
    
    IniService = b
End Function

Private Function WaitForSessionStatus() As Boolean
    
    Dim dt As Date
    
    dt = Now
    
    Do Until m_SessionState <> "" And m_SessionState <> "SessionConnectionUp"
        DoEvents
        If Now > dt + m_TimeOutMilliseconds / 86400000 Then
            Exit Function
        End If
    Loop
    
    WaitForSessionStatus = True
    
End Function

Public Function RequestAuthorization() As Boolean

    Dim b As Boolean
    Dim strToken As String
    
    Dim it As blpapicomLib2.MessageIterator
    Dim msg As blpapicomLib2.Message
    Dim objBlpReq As blpapicomLib2.REQUEST
    Dim element As blpapicomLib2.element
    Dim objEventQueue As blpapicomLib2.EventQueue
    Dim objEvent As blpapicomLib2.Event
    
    If GenerateToken(strToken) Then
    
        If m_AuthorizationService Is Nothing Then
        
            If IniService(m_AuthorizationService, "//blp/apiauth", objBlpReq) Then
                           
                Set objBlpReq = m_AuthorizationService.CreateAuthorizationRequest
                Call objBlpReq.Set("token", strToken)
            
                Set m_Identity = m_Session.CreateIdentity
                Set objEventQueue = m_Session.CreateEventQueue
                
                Call m_Session.SendAuthorizationRequest(objBlpReq, m_Identity, , objEventQueue)
                
                Set objEvent = objEventQueue.NextEvent
                Set it = objEvent.CreateMessageIterator()
                
                Do While it.Next()
                    Set msg = it.Message
                    If msg.MessageTypeAsString = "AuthorizationSuccess" Then
                        ' User passed authorization
                        b = True
                        Exit Do
                    ElseIf msg.MessageTypeAsString = "AuthorizationFailure" Then
                        b = False
                        Exit Do
                    End If
                Loop
                
            End If
        
        End If
        
    End If
    
    RequestAuthorization = b
        
End Function

Public Function GenerateToken(ByRef token As String) As Boolean

    Dim isTokenSuccess As Boolean, isRunning As Boolean
    Dim tokenReqId As CorrelationId
    Dim tokenEventQueue As EventQueue
    Dim it As blpapicomLib2.MessageIterator
    Dim msg As Message
    Dim service As blpapicomLib2.service
    Dim element As blpapicomLib2.element
    Dim EventObj As blpapicomLib2.Event
    
    Set tokenReqId = m_Session.CreateCorrelationId("-9876543210") 'Correlation IDD reserved for Token Generation
    Set tokenEventQueue = m_Session.CreateEventQueue
    
    isTokenSuccess = False
    isRunning = False
    
    Call m_Session.GenerateToken(tokenReqId, tokenEventQueue)
    
    Do While Not isRunning
        
        Set EventObj = tokenEventQueue.NextEvent
        
        If EventObj.eventType = TOKEN_STATUS Then
            Set it = EventObj.CreateMessageIterator()
            Do While it.Next()
                Set msg = it.Message
                If msg.MessageTypeAsString = "TokenGenerationSuccess" Then
                    isTokenSuccess = True
                    isRunning = True
                    token = msg.GetElement("token")
                ElseIf msg.MessageTypeAsString = "TokenGenerationFailure" Then
                    isRunning = True
                    token = msg.Print
                End If
            Loop
        End If
    Loop
    
    GenerateToken = isTokenSuccess
    
End Function

Public Function SendRUNZ(ByRef strXML As String, _
                         ByRef vtCookie As Variant, _
                         Optional ByRef strRtnProc As String, _
                         Optional ByRef vtResult As Variant, _
                         Optional ByRef lngTimeOut As Long)

    Dim objCid As blpapicomLib2.CorrelationId
    Dim objBlpReq As clsBlpRequest
    
    Dim objReq As blpapicomLib2.REQUEST
    Dim objSheet As blpapicomLib2.element
        
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_RunzService, "//blp/runs", objBlpReq) Then
    
        Set objReq = m_RunzService.CreateRequest("sendEpsSheet")
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            '.Security = Array("")
            '.Field = vtFldID
            '.FieldMnemonic = vtFldID
            .cookie = vtCookie
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .SubRequests = 1
            '.security = Empty
            'Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
    
        Set objSheet = objReq.GetElement("sheet")
        Call objSheet.SetValue(strXML)
        Call SendRequest(objReq, objBlpReq, vtResult)
        
    End If
    

End Function

Public Function RequestMarketList(ByRef strList As String, _
                                  ByRef vtCookie As Variant, _
                                  Optional ByRef vtFields As Variant, _
                                  Optional ByRef strRtnProc As String, _
                                  Optional ByRef vtResult As Variant, _
                                  Optional ByRef lngTimeOut As Long)

    Dim objCid As blpapicomLib2.CorrelationId
    Dim objBlpReq As clsBlpRequest
    
    Dim objReq As blpapicomLib2.REQUEST
    Dim objSheet As blpapicomLib2.element
        
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_MktListService, "//blp/mktlist", objBlpReq) Then
    
        Set objReq = m_MktListService.CreateRequest("SnapshotRequest")
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = Array(strList)
            .Field = vtFields
            .FieldMnemonic = vtFields
            .cookie = vtCookie
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .SubRequests = 1
            'Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
    
        Call objReq.Set("security", strList)
        Call SendRequest(objReq, objBlpReq, vtResult)
        
    End If
    

End Function

Public Function SubscribeFXAPI(Optional ByRef boolGMT As Boolean) As Boolean
    
    Dim b As Boolean
    Dim objCid As blpapicomLib2.CorrelationId
    Dim objBlpReq As New clsBlpRequest
    
    Call UnsubscribeFXAPI
    
    If (m_FXAPIService Is Nothing) Then
        Call m_Session.OpenService("//blp/fxapisvc")
    End If
    
    Set m_FXAPIService = m_Session.GetService("//blp/fxapisvc")
    Set m_FXAPISubscriptions = m_Session.CreateSubscriptionList()
    
    Set objCid = m_Session.CreateCorrelationId(-1234567890)  'Correlation ID reserved for FXAPI
    Call m_FXAPISubscriptions.AddEx("//blp/fxapisvc/user", , , objCid)
    Call m_Session.Subscribe(m_FXAPISubscriptions)
    
    objBlpReq.GMT = boolGMT
    
    If IsInCollection(m_Requests, CStr(objCid.Value)) Then
        Call m_Requests.Remove(CStr(objCid.Value))
    End If
    Call m_Requests.Add(objBlpReq, CStr(objCid.Value))
    
    b = True
            
    SubscribeFXAPI = b
    
End Function

Public Function UnsubscribeFXAPI() As Boolean
    Dim b As Boolean
    If Not (m_FXAPISubscriptions Is Nothing) Then
        Call m_Session.Unsubscribe(m_FXAPISubscriptions)
        Set m_FXAPISubscriptions = Nothing
        b = True
    End If
    If IsInCollection(m_Requests, CStr(-1234567890)) Then
        Call m_Requests.Remove(CStr(-1234567890))
    End If
    UnsubscribeFXAPI = b
End Function

Public Function SubscribeMktData(ByRef topic As String, _
                                 Optional ByRef vtFields As Variant, _
                                 Optional ByRef vtCookie As Variant, _
                                 Optional ByRef strService As String = "//blp/mktdata", _
                                 Optional ByRef strOptions As String, _
                                 Optional ByRef strRtnProc As String, _
                                 Optional ByRef boolGMT As Boolean)
    
    '# subscribe to market data
    '# specify topic (can be topic string or security id).
    '# optionally may specify fields array if applicable.
    '# subscribe to one topic / security at a time.
    
    Dim objCid As blpapicomLib2.CorrelationId
    Dim objBlpReq As clsBlpRequest
    
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_MktDataService, strService, objBlpReq) Then
        
        'Call ProcessArguments(vtFields)
        
        Set m_MktDataSubscriptions = m_Session.CreateSubscriptionList()
        
        Set objCid = m_Session.CreateCorrelationId(m_count)
        If objBlpReq.id = BLPREQUEST_ID_NON_INITIALIZED Then
            objBlpReq.id = m_count
        End If
        objBlpReq.ID2 = m_count
        m_count = m_count + 1
        
        If IsArray(vtFields) And strService <> "//blp/mktlist" Then
            If strOptions = "" Then
                Call m_MktDataSubscriptions.AddEx(topic, vtFields, , objCid)
            Else
                Call m_MktDataSubscriptions.AddEx(topic, vtFields, strOptions, objCid)
            End If
        Else
            If strOptions = "" Then
                Call m_MktDataSubscriptions.AddEx(topic, , , objCid)
            Else
                Call m_MktDataSubscriptions.AddEx(topic, , strOptions, objCid)
            End If
        End If
        
        With objBlpReq
            .requestType = "SUBSCRIPTION"
            Call .GetSecurities(Array(topic))
            If IsArray(vtFields) Then
                Call .GetFieldMnemonics(vtFields)
            End If
            .cookie = vtCookie
            .ReturnProcedure = strRtnProc
            m_SubscriptionProcedure = strRtnProc
        End With
        
        If IsInCollection(m_Requests, "sub" & CStr(objCid.Value)) Then
            Call m_Requests.Remove("sub" & CStr(objCid.Value))
        End If
        Call m_Requests.Add(objBlpReq, "sub" & CStr(objCid.Value))
        
        If m_Identity Is Nothing Then
            Call m_Session.Subscribe(m_MktDataSubscriptions)
        Else
            Call m_Session.Subscribe(m_MktDataSubscriptions, m_Identity)
        End If
        
    End If
    
    Set SubscribeMktData = objBlpReq
    
End Function

Public Function UnsubscribeMktData(Optional ByRef CorrelationId As Long = -111) As Boolean
    
    '# if correlationId == -111 then unsubscribe all
    Dim b As Boolean
    Dim sl As blpapicomLib2.SubscriptionList
    Dim it As Long
    Dim cid As blpapicomLib2.CorrelationId
    
    If CorrelationId = -111 Then
        Set sl = m_MktDataSubscriptions
        Set m_MktDataSubscriptions = Nothing
    Else
        Set sl = m_Session.CreateSubscriptionList()
        Set cid = m_Session.CreateCorrelationId(CorrelationId)
        Call sl.Add("", "", cid)
    End If
    
    If Not (sl Is Nothing) Then
        Call m_Session.Unsubscribe(sl)
        b = True
    End If
    
    If CorrelationId = -111 Then
        For it = 0 To m_count Step 1
            If IsInCollection(m_Requests, "sub" & it) Then
                Call m_Requests.Remove("sub" & it)
            End If
        Next it
    Else
        If IsInCollection(m_Requests, "sub" & CStr(CorrelationId)) Then
            Call m_Requests.Remove("sub" & CStr(CorrelationId))
        End If
    End If
    
    UnsubscribeMktData = b
    
End Function

Public Function RequestSecurityLookup(ByRef vtCookie As Variant, _
                                      ByRef strRequestType As String, _
                                      ByRef strQueryString As String, _
                                      ByRef strTickerString As String, _
                                      ByRef boolPartialMatchString As Boolean, _
                                      Optional ByVal vtFields As Variant, _
                                      Optional ByVal lngMaxResultsOption As Long, _
                                      Optional ByRef strYellowKeyFilter As String, _
                                      Optional ByRef strLanguageOverride As String, _
                                      Optional strCountryCode As String, _
                                      Optional strCurrencyCode As String, _
                                      Optional strCurveType As String, _
                                      Optional strCurveSubtype As String, _
                                      Optional ByRef strRtnProc As String, _
                                      Optional ByRef vtResult As Variant, _
                                      Optional ByRef lngTimeOut As Long)
    
    Dim objReq As blpapicomLib2.REQUEST
    Dim objBlpReq As clsBlpRequest
    Dim objElement As blpapicomLib2.element
    
    Set objBlpReq = New clsBlpRequest

    If IniService(m_InstrumentService, "//blp/instruments", objBlpReq) Then
        
        Select Case Trim(strRequestType)
            
            Case "curveListRequest", "govtListRequest", "instrumentListRequest"
        
                Set objReq = m_InstrumentService.CreateRequest(Trim(strRequestType))
        
        End Select

        If Not (objReq Is Nothing) Then
        
            If IsArray(vtFields) = False Then
                If (IsEmpty(vtFields) = False) And (IsMissing(vtFields) = False) Then
                    vtFields = Array(vtFields)
                End If
            End If

            With objBlpReq
                .id = BLPREQUEST_ID_NON_INITIALIZED
                .requestType = strRequestType
                .Field = vtFields
                .FieldMnemonic = vtFields
                .cookie = vtCookie
                .TimeOutMilliseconds = lngTimeOut
                .ReturnProcedure = strRtnProc
                .SubRequests = 1
                .security = Empty
                'Call m_Requests.Add(objBlpReq, CStr(m_Count))
            End With
            
            If strQueryString <> "" Then Call objReq.AsElement().SetElement("query", strQueryString)
            If lngMaxResultsOption <= 0 Then
                lngMaxResultsOption = 500
            End If
            Call objReq.AsElement().SetElement("maxResults", lngMaxResultsOption)
            
            Select Case Trim(strRequestType)
            
                Case "govtListRequest"
                    If strTickerString <> "" Then Call objReq.AsElement().SetElement("ticker", strTickerString)
                    Call objReq.AsElement().SetElement("partialMatch", boolPartialMatchString)
                    
                Case "instrumentListRequest"
                    Select Case Trim(strYellowKeyFilter)
                        Case "YK_FILTER_NONE", "YK_FILTER_CMDT", "YK_FILTER_EQTY", "YK_FILTER_MUNI", "YK_FILTER_PRFD", "YK_FILTER_CLNT", "YK_FILTER_MMKT", "YK_FILTER_GOVT", "YK_FILTER_CORP", "YK_FILTER_INDX", "YK_FILTER_CURR", "YK_FILTER_MTGE"
                            Call objReq.AsElement().SetElement("yellowKeyFilter", Trim(strYellowKeyFilter))
                    End Select
                    Select Case Trim(strLanguageOverride)
                        Case "LANG_OVERRIDE_NONE", "LANG_OVERRIDE_ENGLISH", "LANG_OVERRIDE_KANJI", "LANG_OVERRIDE_FRENCH", "LANG_OVERRIDE_GERMAN", "LANG_OVERRIDE_SPANISH", "LANG_OVERRIDE_PORTUGUESE", "LANG_OVERRIDE_ITALIAN", "LANG_OVERRIDE_CHINESE_TRAD", "LANG_OVERRIDE_KOREAN", "LANG_OVERRIDE_CHINESE_SIMP", "LANG_OVERRIDE_NONE_1", "LANG_OVERRIDE_NONE_2", "LANG_OVERRIDE_NONE_3", "LANG_OVERRIDE_NONE_4", "LANG_OVERRIDE_NONE_5", "LANG_OVERRIDE_RUSSIAN"
                            Call objReq.AsElement().SetElement("languageOverride", Trim(strLanguageOverride))
                    End Select
                    
                Case "curveListRequest"
                    If Len(Trim(strCountryCode)) = 2 Then
                         Call objReq.AsElement().SetElement("countryCode", Trim(strCountryCode))
                    End If
                    If Len(Trim(strCurrencyCode)) = 3 Then
                         Call objReq.AsElement().SetElement("currencyCode", Trim(strCurrencyCode))
                    End If
                    Select Case Trim(strCurveType)
                        Case "INVALID", "UNASSIGNED", "IRS", "GOVT", "AGENCY", "MUNI", "CORP", "MTGE", "MMKT", "CURNCY", "COMDTY"
                            Call objReq.AsElement().SetElement("type", strCurveType)
                    End Select
                    Select Case Trim(strCurveSubtype)
                        Case "INVALID", "UNASSIGNED", "SENIOR", "SUBORDINATED", "ZERO", "OIS", "INFLATION", "SPREAD", "CDS", "RATE", "SECTOR"
                            Call objReq.AsElement().SetElement("subtype", Trim(strCurveSubtype))
                    End Select
                    
            End Select
           
            Call SendRequest(objReq, objBlpReq, vtResult)
        
        End If
        
    End If

    Set RequestSecurityLookup = objBlpReq

End Function

Public Function RequestFieldInfo(ByRef vtFldID As Variant, _
                                 ByRef vtCookie As Variant, _
                                 Optional ByRef boolReturnFieldDocumentation As Boolean, _
                                 Optional ByRef boolReturnIfGetHeader As Boolean, _
                                 Optional ByRef boolReturnIfOverridable As Boolean, _
                                 Optional ByRef strRtnProc As String, _
                                 Optional ByRef vtResult As Variant, _
                                 Optional ByRef lngTimeOut As Long) As clsBlpRequest


    Dim objReq As blpapicomLib2.REQUEST
    Dim objElement As blpapicomLib2.element
    Dim objBlpReq As clsBlpRequest
    Dim k As Long
    Dim s As String
        
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_FieldInfoService, "//blp/apiflds", objBlpReq) Then
        
        Call ProcessArguments(vtFldID)
        'If IsArray(vtFldID) = False Then vtFldID = Array(vtFldID)
    
        Set objReq = m_FieldInfoService.CreateRequest("FieldInfoRequest")
           
        Set objElement = objReq.GetElement("id")
        For k = LBound(vtFldID) To UBound(vtFldID)
            Call objElement.AppendValue(Trim(CStr(vtFldID(k))))
        Next k
        
        If boolReturnFieldDocumentation Then
            s = "true"
        Else
            s = "false"
        End If
        Call objReq.Set("returnFieldDocumentation", s)
        
        If boolReturnIfGetHeader Then
            Set objElement = objReq.GetElement("properties")
            Call objElement.AppendValue("apigetheader")
        End If
        If boolReturnIfOverridable Then
            Set objElement = objReq.GetElement("properties")
            Call objElement.AppendValue("fieldoverridable")
        End If
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            '.Security = Array("")
            .Field = vtFldID
            .FieldMnemonic = vtFldID
            .cookie = vtCookie
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .SubRequests = 1
            .security = Empty
            'Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
    
        Call SendRequest(objReq, objBlpReq, vtResult)
        
        
    End If
    
    Set RequestFieldInfo = objBlpReq

End Function

Public Function RequestBEQSData(ByRef strScreenName As String, _
                                ByRef vtCookie As Variant, _
                                Optional ByRef vtFields As Variant, _
                                Optional ByVal strScreenType As String, _
                                Optional ByVal strFolder As String, _
                                Optional ByRef strLanguage As String, _
                                Optional ByRef boolDisplayHeader As Boolean, _
                                Optional ByRef strRtnProc As String, _
                                Optional ByRef vtResult As Variant, _
                                Optional ByRef lngTimeOut As Long, _
                                Optional ByRef sortField As String) As clsBlpRequest
    
    'Screen Type Options: GLOBAL, PRIVATE
    Dim objReq As blpapicomLib2.REQUEST
    Dim objBlpReq As clsBlpRequest
    
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_RefDataService, "//blp/refdata", objBlpReq) Then
    
        If Trim(strScreenType) = "" Then strScreenType = "PRIVATE"
        If Trim(strFolder) = "" Then strFolder = "General"
        
        Dim vtFieldsOriginal As Variant
        vtFieldsOriginal = vtFields
        
        Call ProcessArguments(vtFields)
    
        Set objReq = m_RefDataService.CreateRequest("BeqsRequest")
        Call objReq.Set("screenName", strScreenName)
        Call objReq.Set("screenType", strScreenType)
        Call objReq.Set("Group", strFolder)
        If Trim(strLanguage) <> "" Then
            Call objReq.Set("languageId", UCase(Trim(strLanguage)))
        End If
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = Array(strScreenName)
            .Field = vtFields
            .FieldMnemonic = vtFields
            .cookie = vtCookie
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .DisplayHeader = boolDisplayHeader
            .sortField = sortField
            .SubRequests = 1
           ' Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
    
        Call SendRequest(objReq, objBlpReq, vtResult)
    
    End If
    
    Set RequestBEQSData = objBlpReq

End Function

Public Function RequestBSRCHData(ByRef strDomain As String, _
                                 ByRef vtCookie As Variant, _
                                 Optional ByRef vtFields As Variant, _
                                 Optional ByRef vtOvFields As Variant, _
                                 Optional ByRef vtOvValues As Variant, _
                                 Optional ByRef boolDisplayHeader As Boolean, _
                                 Optional ByRef strRtnProc As String, _
                                 Optional ByRef vtResult As Variant, _
                                 Optional ByRef boolMergeResultArrays As Boolean = True, _
                                 Optional ByRef lngTimeOut As Long, _
                                 Optional ByRef sortField As String, _
                                 Optional ByRef sortOrder As Boolean = False) As clsBlpRequest
'--------------------------------------------------------------------
' Function  : RequestBSRCHData
' Author    : Dhaval Maheshwar
' Date      : 2013/12/01
' Purpose   : Encapsulates parameters into a class clsBlpRequest object that will be used to
'               requests SRCH data. This is used to get bonds /loans in FI, or vessel info in CMDTY
' Returns: clsBlpRequest
'
' Parameters:
'       strDomain       (I): variant containing list of securities to be requested (can contain a single security)
'       vtCookie        (I): Cookie (ID) for the request
'       vtFields        (I): variant containing list of fields
'       vtOvFields      (I): fields to be overriden, if any
'       vtOvValues      (I): value for override fields
'       boolDisplayHeader   (I): TRUE will display the data header
'       strRtnProc          (I): Use this paramater if you want to force a return procedure to use
'       vtResult            (O): if empty, the procedure will be asynchronous
'                                if not , this variant will contain the data returned
'       boolMergeResultArrays      (I): merge results in a single array
'       lngTimeOut                 (I): if procedure is asynchronous, define the timeout (in milliseconds)
'       sortField                  (I): Choose a field to sort from (only commodities now)
'       sortOrder                  (I): Ascending or descending
'
' Last updated :
' By :
'------------------------------------------------------------------
 
    
    
    'Screen Type Options: GLOBAL, PRIVATE
    Dim objReq As blpapicomLib2.REQUEST
    Dim objBlpReq As clsBlpRequest
    
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_SearchService, "//blp/exrsvc", objBlpReq) Then
    
        Call ProcessArguments(vtFields)
    
        Set objReq = m_SearchService.CreateRequest("ExcelGetGridRequest")
        Call objReq.Set("Domain", strDomain)
        Call AddOverrides(objReq, vtOvFields, vtOvValues)
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = Array(strDomain)
            .Field = vtFields
            .FieldMnemonic = vtFields
            .cookie = vtCookie
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .DisplayHeader = boolDisplayHeader
            .sortField = sortField
            .sortOrder = sortOrder
            .SubRequests = 1
            .MergeArrays = boolMergeResultArrays
          
           ' Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
    
        Call SendRequest(objReq, objBlpReq, vtResult)
    
    End If
    
    Set RequestBSRCHData = objBlpReq

End Function

Public Function RequestPortfolioData(ByRef vtSecurities As Variant, _
                                     ByRef vtCookie As Variant, _
                                     ByRef vtFields As Variant, _
                                     Optional ByRef vtOvFields As Variant, _
                                     Optional ByRef vtOvValues As Variant, _
                                     Optional ByRef strRtnProc As String, _
                                     Optional ByRef vtResult As Variant, _
                                     Optional ByRef lngTimeOut As Long, _
                                     Optional ByRef boolShowBulkHeaders As Boolean, _
                                     Optional ByRef vtFiller As Variant) As clsBlpRequest
    Set RequestPortfolioData = RequestStaticData("PortfolioDataRequest", vtSecurities, vtCookie, vtFields, vtOvFields, vtOvValues, , strRtnProc, vtResult, lngTimeOut, , , , boolShowBulkHeaders, False, vtFiller)
End Function

Public Function RequestReferenceData(ByRef vtSecurities As Variant, _
                                     ByRef vtCookie As Variant, _
                                     ByRef vtFields As Variant, _
                                     Optional ByRef vtOvFields As Variant, _
                                     Optional ByRef vtOvValues As Variant, _
                                     Optional ByRef strRtnProc As String, _
                                     Optional ByRef vtResult As Variant, _
                                     Optional ByRef lngTimeOut As Long, _
                                     Optional ByRef fillBdpIfRealtime As Boolean = False, _
                                     Optional ByRef referenceTickerLocation As Range = Nothing, _
                                     Optional ByRef addItionalBDPOption As String = "", _
                                     Optional ByRef boolShowBulkHeaders As Boolean, _
                                     Optional ByRef boolReturnNullValue As Boolean = True, _
                                     Optional ByRef vtFiller As Variant) As clsBlpRequest
    Set RequestReferenceData = RequestStaticData("ReferenceDataRequest", vtSecurities, vtCookie, vtFields, vtOvFields, vtOvValues, , strRtnProc, vtResult, lngTimeOut, fillBdpIfRealtime, referenceTickerLocation, addItionalBDPOption, boolShowBulkHeaders, boolReturnNullValue, vtFiller)
End Function

Private Sub ProcessArguments(ParamArray vtInputs() As Variant)
    
    Dim k As Long
    
    If IsArray(vtInputs) Then
        For k = LBound(vtInputs) To UBound(vtInputs)
            vtInputs(k) = ProcessArgument(vtInputs(k))
        Next k
    End If

End Sub

Private Function ProcessArgument(ByRef vtInput As Variant) As Variant

    Dim v As Variant
    Dim r As Range
    
    If TypeName(vtInput) = "Range" Then
        Set r = vtInput
        v = modValidation.LoadList(r, True, False)
    ElseIf IsMissing(vtInput) = True Then
        v = vtInput
    ElseIf IsArray(vtInput) = False Then
        v = Array(vtInput)
    Else
        v = vtInput
    End If
    
    ProcessArgument = v
    
End Function


'--------------------------------------------------------------------
' Function: RequestStaticData
' Module:   clsBlpApi
' Author:   xberard
' Date:     2010/01/01
' Purpose:  Requests data for RequestPortfolioData() and RequestReferenceData()
'
' Returns: Instance of clsBlpRequest
'
' Parameters:
'   strRequestType          (i): The type of static data request type.  Currently "PortfolioDataRequest", "ReferenceDataRequest" and
'                                 are passed in from RequestPortfolioData() and RequestReferenceData() respectively.
'   vtSecurities            (i): A string or variant containing the ticker(s)/portfolio id(s) for which data is being requested.
'   vtCookie                (i): Cookie (ID) for the request.
'   vtFields                (i): The field(s) being requested.
'   vtOvFields              (i): Override field(s) being requested.
'   vtOvValues              (i): Override value(s) for the override fields.
'   strCurrency             (i): CANNOT BE USED(?).  Sets the "currency" item in the request object, using the 3 letter ISO code.
'                                View WCV<GO> for a list of currencies.  This is only applied when strRequestType is not equal to
'                                "CustomEqsRequest."  Currently, there do not appear to be any functions that call this function with
'                                this request type.
'   strRtnProc              (i): ???
'   vtResult                (o): Variant which will hold the results from the request in the event of a synchronous request.  For
'                                asynchronous requests, no variable is passed.
'   lngTimeOut              (i): Request timeout in milliseconds.
'   fillBdpIfRealtime       (i): ???
'   referenceTickerLocation (i): ???
'   addItionalBDPOption     (i): ???
'   boolShowBulkHeaders     (i): ???
'   boolReturnNullValue     (i): ???
'   vtFiller                (i): ???
'
' Last updated: 2014/01/21
' By:           jlalancette
'------------------------------------------------------------------
Private Function RequestStaticData(ByRef strRequestType As String, _
                                   ByVal vtSecurities As Variant, _
                                   ByRef vtCookie As Variant, _
                                   ByVal vtFields As Variant, _
                                   Optional ByVal vtOvFields As Variant, _
                                   Optional ByVal vtOvValues As Variant, _
                                   Optional ByRef strCurrency As String, _
                                   Optional ByRef strRtnProc As String, _
                                   Optional ByRef vtResult As Variant, _
                                   Optional ByRef lngTimeOut As Long, _
                                   Optional ByRef fillBdpIfRealtime As Boolean = False, _
                                   Optional ByRef referenceTickerLocation As Range = Nothing, _
                                   Optional ByRef addItionalBDPOption As String = "", _
                                   Optional ByRef boolShowBulkHeaders As Boolean, _
                                   Optional ByRef boolReturnNullValue As Boolean = True, _
                                   Optional ByRef vtFiller As Variant) As clsBlpRequest
    
    Dim k As Long                                   '// For looping
    Dim objReq As blpapicomLib2.REQUEST
    Dim obj As blpapicomLib2.element
    Dim objOverrides As blpapicomLib2.element
    Dim objEvent  As blpapicomLib2.Event
    Dim objBlpReq As clsBlpRequest
    Dim ticker As Variant
    
    Dim vtFieldRealtimeMapping As Variant
    Dim vtUniqueFields As Variant
    Dim numberOfFieldRequested As Long              '// Used to determine "isFakeRequest" for SendRequest()
    
    'Dim i As Long                                   '// Looks unused
    'Dim objOverride  As blpapicomLib2.Element       '// Looks unused
    'Dim objCorr As blpapicomLib2.CorrelationId      '// Looks unused
    'Dim numOfSec As Long                            '// Not needed?
    
    Set objBlpReq = New clsBlpRequest
    
    '// Attempt to initialize the service.
    If IniService(m_RefDataService, "//blp/refdata", objBlpReq) Then
        '// Make sure that the arguments are in a format that is acceptable for the API.
        Call ProcessArguments(vtSecurities, vtFields, vtOvFields, vtOvValues)
        
        '// If the fillBdpIfRealtime flag is on, find out which fields are realtime fiels.
        If fillBdpIfRealtime Then
            vtFieldRealtimeMapping = modValidation.areRealTimeFields(vtFields)
        End If
        
        '// Create the request using the request type passed in.
        Set objReq = m_RefDataService.CreateRequest(strRequestType)
        
        '// Set values for the request object
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .GetSecurities vtSecurities                     '// Set the securities to request?  (check logic of GetSecurities => ProcessArrayInput)
            .Field = vtFields                               '// Set the fields to request
            .RealTimeFieldMapping = vtFieldRealtimeMapping  '// Set the realtime field mapping using the array of boolean values set above.
            
            '// Process the array of fields (not realtime) and retrieve a list of unique fields.
            vtFields = ProcessFieldsArray(vtFields, False, , vtUniqueFields)
            vtOvFields = ProcessFieldsArray(vtOvFields, False)      '// Process the override fields with the realtime flag set to false.
            
            .FieldMnemonic = vtFields                       '// Set the field mnemonics
            .OverrideFieldMnemonic = vtOvFields             '// Set the override field mneumonics
            .OverrideFieldValue = vtOvValues                '// Set the override field values
            .cookie = vtCookie                              '// Set the cookie/request identifier
            .TimeOutMilliseconds = lngTimeOut               '// Set the timeout wait time
            .ReturnProcedure = strRtnProc                   '// ???
            .SubRequests = 1                                '// ???
            .FillBDPForRTField = fillBdpIfRealtime          '// ???
            .AdditionalBDPOptions = addItionalBDPOption     '// ???
            .ShowBulkHeader = boolShowBulkHeaders           '// Display headers in the response (?)
            .Filler = vtFiller                              '// Set the filler
            Set .referenceTickerLocation = referenceTickerLocation  '// ???
            'Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
        
        Set obj = objReq.GetElement("securities")           '// Get an object pointing to the securities element of the request.
        'numOfSec = 0
        For Each ticker In objBlpReq.RequestedSecurity      '// Loop through each security...
            obj.AppendValue ticker                          '// ...and add it to the security element in the request.
            'numOfSec = numOfSec + 1
        Next 'ticker
        'If numOfSec = 0 Then
        '    Exit Function
        'End If
        
        numberOfFieldRequested = 0                          '// Variable will be 0 by default, but reset it to be safe.
        Set obj = objReq.GetElement("fields")               '// Get an object pointing to the fields element of the request.
        
        For k = LBound(vtUniqueFields) To UBound(vtUniqueFields)            '// Loop through each unique field
            If Trim(CStr(vtUniqueFields(k))) <> "" Then                     '// Make sure the value is not blank
                If fillBdpIfRealtime Then                                   '// ???
                    If Not vtFieldRealtimeMapping(k) Then                   '// Make sure the field isn't realtime.
                        numberOfFieldRequested = numberOfFieldRequested + 1 '// Increment the number of fields requested
                        Call obj.AppendValue(CStr(vtUniqueFields(k)))       '// and append it to the list of fields.
                    End If
                Else
                    numberOfFieldRequested = numberOfFieldRequested + 1     '// Increment the number of fields requested
                    Call obj.AppendValue(CStr(vtUniqueFields(k)))           '// and append it to the list of fields.
                End If
            End If
        Next 'k
        
        '// Currently, there appears to be no case where strRequestType would be equal to "CustomEqsRequest", so...
        If strRequestType <> "CustomEqsRequest" Then            '// This case is always executed...
            Call AddOverrides(objReq, vtOvFields, vtOvValues)   '// Apply overrides
        ElseIf strCurrency <> "" Then                           '// ...and this case is never executed?
            Call objReq.Set("currency", strCurrency)            '// Apply currency
        End If
        
    '    Call objReq.Set("returnFormattedValue", False)
    '    Call objReq.Set("useUTCTime", True)
        If strRequestType <> "PortfolioDataRequest" Then
            Call objReq.Set("returnNullValue", boolReturnNullValue)
        End If
        
        '// Send the request
        Call SendRequest(objReq, objBlpReq, vtResult, (numberOfFieldRequested = 0 And fillBdpIfRealtime)) ' Or (numOfSec = 0))
    End If
    
    Set RequestStaticData = objBlpReq   '// Return the request object
End Function


Private Sub AddOverrides(ByRef objReq As blpapicomLib2.REQUEST, ByRef vtOvFields As Variant, ByRef vtOvValues As Variant)
    
    Dim j As Long, k As Long
    Dim objOverrides As blpapicomLib2.element
    Dim objOverride  As blpapicomLib2.element
    Dim strOvEltName As String, strOvName As String, strOvValue As String
    
    Select Case objReq.AsElement.Name
        Case "ExcelGetGridRequest"
            strOvEltName = "Overrides"
            strOvName = "name"
            strOvValue = "value"
        Case Else
            strOvEltName = "overrides"
            strOvName = "fieldId"
            strOvValue = "value"
    End Select
    
    If HasValidOverrides(vtOvFields, vtOvValues, j) Then
        Set objOverrides = objReq.GetElement(strOvEltName)
        For k = LBound(vtOvFields) To UBound(vtOvFields)
            If Trim(vtOvFields(k)) <> "" Then
                If Trim(vtOvValues(k)) <> "" Then
                    Set objOverride = objOverrides.AppendElment()
                    Call objOverride.SetElement(strOvName, UCase(Replace(vtOvFields(k), " ", "_")))
                    Call objOverride.SetElement(strOvValue, ModifyParameter(vtOvValues(k - j), True, True))
                End If
            End If
        Next k
    End If
    
End Sub

Private Function ModifyParameter(ByVal v As Variant, ByRef boolFormatDatesAsYYYYMMDD As Boolean, ByRef boolForceStrings As Boolean) As Variant
    
    'This function cleans up parameters used as Overrides or TASVC study parameters
    
    Dim s As String
    
    If VarType(v) = 8 Or (IsNumeric(v) And boolForceStrings) Then
        s = Trim(CStr(v))
        If IsNumeric(v) Then
            s = Replace(s, Application.ThousandsSeparator, "")
            s = Replace(s, Application.DecimalSeparator, ".")
        ElseIf IsDate(v) And boolFormatDatesAsYYYYMMDD Then
            s = Format(CDate(s), "YYYYMMDD")
        End If
        v = s
    ElseIf VarType(v) = 7 And boolFormatDatesAsYYYYMMDD Then
        s = Format(CDate(v), "YYYYMMDD")
        v = s
    End If

    ModifyParameter = v
    
End Function

Public Function RequestHistoricalData(ByVal vtSecurities As Variant, _
                                      ByRef vtCookie As Variant, _
                                      ByVal vtFields As Variant, _
                                      ByVal vtStartDate As Variant, Optional ByVal vtEndDate As Variant, _
                                      Optional ByVal vtOvFields As Variant, Optional ByVal vtOvValues As Variant, _
                                      Optional ByRef lngMaxDataPoints As Long, _
                                      Optional ByRef strCurrency As String, _
                                      Optional ByRef strPeriodicityAdjustment As String, _
                                      Optional ByRef strPeriodicitySelection As String, _
                                      Optional ByRef strNonTradingDayFillOption As String, Optional ByRef strNonTradingDayFillMethod As String, _
                                      Optional ByVal strCalendarCodeOverride As String, _
                                      Optional ByRef strOverrideOption As String, _
                                      Optional ByRef strPricingOption As String, _
                                      Optional ByRef vtAdjustmentFollowDPDF As Variant, Optional ByRef vtAdjustmentSplit As Variant, _
                                      Optional ByRef vtAdjustmentAbnormal As Variant, Optional ByRef vtAdjustmentNormal As Variant, _
                                      Optional ByRef boolReverseChronological As Boolean, _
                                      Optional ByRef boolDisplayHorizontal As Boolean, Optional ByRef boolSkipFirstFieldExceptFirstRow As Boolean, _
                                      Optional ByRef boolConvertDatesTorStringBefore1900 As Boolean, _
                                      Optional ByRef strRtnProc As String, _
                                      Optional ByRef vtResult As Variant, _
                                      Optional ByRef lngTimeOut As Long, _
                                      Optional ByRef boolMergeResultArrays As Boolean = True, _
                                      Optional ByRef vtReturnFundamentalPeriodicDateFormat As Variant) As clsBlpRequest
'--------------------------------------------------------------------
' Function  : RequestHistoricalData
' Author    : Xavier Berard
' Date      : 2010/01/01
' Purpose   : Encapsulates parameters into a class clsBlpRequest object that will be used to
'               requests historical data
'
' Returns: clsBlpRequest
'
' Parameters:
'       vtSecurities    (I): variant containing list of securities to be requested (can contain a single security)
'       vtCookie        (I): Cookie (ID) for the request
'       vtFields        (I): variant containing list of fields
'       vtStartDate     (I): start of the analysis (format: #12/31/2015#)
'       vtEndDate       (I): end of the analysis (format: #12/31/2015#)
'       vtOvFields      (I): fields to be overriden, if any
'       vtOvValues      (I): value for override fields
'       lngMaxDataPoints    (I): (equivalent of Points= parameter in =BDH())
'       strCurrency         (I):
'       strPeriodicityAdjustment    (I): available values ACTUAL, CALENDAR, FISCAL
'       strPeriodicitySelection     (I): available values DAILY, WEEKLY, MONTHLY, QUARTERLY, SEMI_ANNUALLY, YEARLY
'       strNonTradingDayFillOption  (I): available values NON_TRADING_WEEKDAYS, ALL_CALENDAR_DAYS , ACTIVE_DAYS_ONLY
'       strNonTradingDayFillMethod  (I): available values PREVIOUS_VALUE, NIL_VALUE
'                                           (equivalent of Fill= parameter in =BDH())
'       strCalendarCodeOverride     (I): Applies specified settlement calendar to history formula.
'                                           The available codes correspond to CDR<GO>.  Multiple calendar codes are supported.
'                                           The CDR override is only valid for daily periodicity. When using the CDR option with PER=W,
'                                           an Invalid Parameter error is displayed.
'       strOverrideOption           (I): available values OVERRIDE_OPTION_CLOSE, OVERRIDE_OPTION_GPA
'       strPricingOption            (I): available values PRICING_OPTION_PRICE, PRICING_OPTION_YIELD
'       vtAdjustmentFollowDPDF      (I): follows DPDF settings
'       vtAdjustmentSplit           (I): DPDF settings, Whether to use pricing defaults for distributions. All other options are ignored.
'       vtAdjustmentAbnormal        (I): DPDF settings, Cash Adjustment Abnormal.
'                                           Adjust to reflect: Special Cash, Liquidation, Capital Gains,
'                                           Long-Term Capital Gains, Short-Term Capital Gains, Memorial,
'                                           Return of Capital, Rights Redemption, Miscellaneous, Return Premium,
'                                           Preferred Rights Redemption, Proceeds/Rights, Proceeds/Shares, Proceeds/Warrants.
'       vtAdjustmentNormal          (I): DPDF settings, Cash Adjustment Normal.
'                                           Adjust  to reflect: Regular Cash, Interim, 1st Interim, 2nd Interim, 3rd Interim,
'                                           4th Interim, 5th Interim, Income, Estimated, Partnership Distribution, Final,
'                                           Interest on Capital, Distribution, Prorated.
'       boolReverseChronological    (I): TRUE will put newer data first
'       boolDisplayHorizontal       (I): TRUE will arrange the data horizontally
'       boolSkipFirstFieldExceptFirstRow    (I):
'       boolConvertDatesTorStringBefore1900 (I):
'       strRtnProc          (I): Use this paramater if you want to force a return procedure to use
'       vtResult            (O): if empty, the procedure will be asynchronous
'                                if not , this variant will contain the data returned
'       lngTimeOut                  (I): if procedure is asynchronous, define the timeout (in milliseconds)
'       boolMergeResultArrays       (I): merge results in a single array
'       vtReturnFundamentalPeriodicDateFormat   (I):
'
' Last updated :
' By :
'------------------------------------------------------------------


    Dim k As Long, numOfSec As Long
    Dim objReq As blpapicomLib2.REQUEST
    Dim objOverrides As blpapicomLib2.element
    Dim objOverride  As blpapicomLib2.element
    Dim objCDRs As blpapicomLib2.element
    Dim objCDR As blpapicomLib2.element
    Dim objBlpReq As clsBlpRequest
    Dim vtString As Variant, vtStringVal As Variant, vtBool As Variant, vtBoolVal As Variant
    Dim vtCDR As Variant, strCDR As String
    
    'periodicityAdjustment:     ACTUAL, CALENDAR, FISCAL
    'periodicitySelection :     DAILY, WEEKLY, MONTHLY, QUARTERLY, SEMI_ANNUALLY, YEARLY
    'overrideOption:            OVERRIDE_OPTION_CLOSE, OVERRIDE_OPTION_GPA
    'pricingOption :            PRICING_OPTION_PRICE, PRICING_OPTION_YIELD
    'nonTradingDayFillOption:   NON_TRADING_WEEKDAYS, ALL_CALENDAR_DAYS , ACTIVE_DAYS_ONLY
    'nonTradingDayFillMethod:   PREVIOUS_VALUE, NIL_VALUE
    
    
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_RefDataService, "//blp/refdata", objBlpReq) Then
    
        vtString = Array("currency", "periodicityAdjustment", "periodicitySelection", "nonTradingDayFillOption", "nonTradingDayFillMethod", "overrideOption", "pricingOption") '"calendarCodeOverride",
        vtStringVal = Array(strCurrency, strPeriodicityAdjustment, strPeriodicitySelection, strNonTradingDayFillOption, strNonTradingDayFillMethod, strOverrideOption, strPricingOption)  'strCalendarCodeOverride,
        vtBool = Array("returnRelativeDate", "returnDataIndicator", "returnFundamentalPeriodicDateFormat", "adjustmentFollowDPDF", "adjustmentSplit", "adjustmentAbnormal", "adjustmentNormal")
        vtBoolVal = Array(False, False, vtReturnFundamentalPeriodicDateFormat, vtAdjustmentFollowDPDF, vtAdjustmentSplit, vtAdjustmentAbnormal, vtAdjustmentNormal)

        Call ProcessArguments(vtSecurities, vtFields, vtOvFields, vtOvValues)
        
        If IsDate(vtStartDate) Then vtStartDate = Format(CDate(vtStartDate), "YYYYMMDD")
        If IsMissing(vtEndDate) Then vtEndDate = Date
        If IsDate(vtEndDate) Then vtEndDate = Format(CDate(vtEndDate), "YYYYMMDD")
        
        Set objReq = m_RefDataService.CreateRequest("HistoricalDataRequest")
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = vtSecurities
            .Field = vtFields
            vtFields = ProcessFieldsArray(vtFields, False, vtBoolVal)
            vtOvFields = ProcessFieldsArray(vtOvFields, False, vtBoolVal)
            .FieldMnemonic = vtFields
            .OverrideFieldMnemonic = vtOvFields
            .OverrideFieldValue = vtOvValues
            .cookie = vtCookie
            .ConvertDatesTorStringBefore1900 = boolConvertDatesTorStringBefore1900
            .DisplayHorizontal = boolDisplayHorizontal
            .ReverseChronological = boolReverseChronological
            .SkipFirstFieldExceptFirstRow = boolSkipFirstFieldExceptFirstRow
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .MergeArrays = boolMergeResultArrays
            .SubRequests = 1
            'Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
        
        numOfSec = 0
        For k = LBound(vtSecurities, 1) To UBound(vtSecurities, 1)
             If Trim(CStr(vtSecurities(k))) <> "" Then
                  Call objReq.GetElement("securities").AppendValue(CStr(vtSecurities(k)))
                  numOfSec = numOfSec + 1
             End If
        Next k
        
        For k = LBound(vtFields, 1) To UBound(vtFields, 1)
            Select Case Replace(UCase(Trim(vtFields(k))), " ", "_")
                Case "DATE", "RELATIVE_DATE", "DATA_INDICATOR"
                Case Else
                    Call objReq.GetElement("fields").AppendValue(CStr(vtFields(k)))
            End Select
        Next k
        
        Call AddOverrides(objReq, vtOvFields, vtOvValues)
        
        Call objReq.Set("startDate", CStr(vtStartDate))
        Call objReq.Set("endDate", CStr(vtEndDate))
        If lngMaxDataPoints > 0 Then Call objReq.Set("maxDataPoints", CStr(lngMaxDataPoints))
        
        For k = LBound(vtStringVal) To UBound(vtStringVal)
            If CStr(vtStringVal(k)) <> "" Then
                Call objReq.Set(CStr(vtString(k)), CStr(vtStringVal(k)))
            End If
        Next k
        
        For k = LBound(vtBool) To UBound(vtBool)
            If IsMissing(vtBoolVal(k)) = False Then
                Call objReq.Set(CStr(vtBool(k)), CBool(vtBoolVal(k)))
            End If
        Next k
        
        strCalendarCodeOverride = Trim(strCalendarCodeOverride)
        If strCalendarCodeOverride <> "" Then
            Set objCDRs = objReq.GetElement("calendarOverridesInfo")
            Set objCDR = objCDRs.GetElement("calendarOverrides")
            If InStr(1, strCalendarCodeOverride, "|") > 1 Then
                Call objCDRs.SetElement("calendarOverridesOperation", "CDR_OR")
                vtCDR = Split(strCalendarCodeOverride, "|")
            Else 'If InStr(1, strCalendarCodeOverride, "|") > 1 Then
                Call objCDRs.SetElement("calendarOverridesOperation", "CDR_AND")
                vtCDR = Split(strCalendarCodeOverride, "&")
            End If
            For k = LBound(vtCDR) To UBound(vtCDR)
                strCDR = Trim(vtCDR(k))
                If strCDR <> "" Then
                    Call objCDR.AppendValue(strCDR)
                End If
            Next k
        End If
    
        Call SendRequest(objReq, objBlpReq, vtResult, numOfSec = 0)
        
    End If
        
    Set RequestHistoricalData = objBlpReq
      
End Function

Public Function RequestIntradayBarData(ByVal vtSecurity As Variant, _
                                       ByRef vtCookie As Variant, _
                                       ByVal vtEvents As Variant, _
                                       ByVal vtFields As Variant, _
                                       ByRef dtStartDate As Date, _
                                       Optional ByVal dtEndDate As Date, _
                                       Optional ByVal lngInterval As Long, _
                                       Optional ByRef vtFillInitialBar As Variant, _
                                       Optional ByRef vtAdjustmentFollowDPDF As Variant, _
                                       Optional ByRef vtAdjustmentSplit As Variant, _
                                       Optional ByRef vtAdjustmentAbnormal As Variant, _
                                       Optional ByRef vtAdjustmentNormal As Variant, _
                                       Optional ByRef lngMaxDataPoints As Long, _
                                       Optional ByRef boolReverseChronological As Boolean, _
                                       Optional ByRef boolDisplayHorizontal As Boolean, _
                                       Optional ByRef boolGMT As Boolean, _
                                       Optional ByRef strRtnProc As String, _
                                       Optional ByRef vtResult As Variant, _
                                       Optional ByRef lngTimeOut As Long, _
                                       Optional ByRef boolMergeResultArrays As Boolean = True, _
                                       Optional ByRef strDefaultFillMethod As String, _
                                       Optional ByRef boolTheSameTimeFrameEveryDay = False) As clsBlpRequest
                                  
    'eventType: TRADE, BID, ASK, BID_BEST, ASK_BEST, BID_YIELD, ASK_YIELD, MID_PRICE, AT_TRADE, BEST_BID, BEST_ASK
    'fields: time, open, high, low, close, volume, numEvents
    
    Dim i As Long, j As Long, k As Long
    Dim objReq As blpapicomLib2.REQUEST '
    Dim objBlpReq As clsBlpRequest
    Dim vtBool As Variant, vtBoolVal As Variant
    Dim tmpStartTime As Double, tmpEndTime As Double
    Dim dayLightSavingAdj As Long
    Dim lb As Long, ub As Long
    Dim objDateTimeDuration As blpapicomLib2.element
    Dim objDateTimeDurations As blpapicomLib2.element
    Dim duration As Long
   
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_RefDataService, "//blp/refdata", objBlpReq) Then
    
        'set IsFillIntradayBar here since strDefaultFillMethod might be "" due to the following code
        objBlpReq.IsFillIntradayBar = Trim(strDefaultFillMethod) <> ""
        'always get the initial bar for "Previous" fill
        If Trim(strDefaultFillMethod) = "P" Or Trim(strDefaultFillMethod) = "C" Or Trim(strDefaultFillMethod) = "Previous" Then
            vtFillInitialBar = True
            strDefaultFillMethod = "P"
        End If
        'change strDefaultFillMethod accordingly to have faster performance and clear code later
        If Trim(strDefaultFillMethod) = "N" Or Trim(strDefaultFillMethod) = "E" Or Trim(strDefaultFillMethod) = "Error" Then strDefaultFillMethod = "#N/A N/A"
        If Trim(strDefaultFillMethod) = "B" Or Trim(strDefaultFillMethod) = "Blank" Then strDefaultFillMethod = ""
            
        vtBool = Array("gapFillInitialBar", "adjustmentFollowDPDF", "adjustmentSplit", "adjustmentAbnormal", "adjustmentNormal")
        vtBoolVal = Array(vtFillInitialBar, vtAdjustmentFollowDPDF, vtAdjustmentSplit, vtAdjustmentAbnormal, vtAdjustmentNormal)
        
        If lngInterval < 1 Then lngInterval = 1
        If CDbl(dtEndDate) = 0 Then dtEndDate = Now
        
        Call ProcessArguments(vtSecurity, vtFields, vtEvents)
        
        If boolTheSameTimeFrameEveryDay Then
            Set objReq = m_RefDataService.CreateRequest("IntradayBarDateTimeChoiceRequest")
        Else
            Set objReq = m_RefDataService.CreateRequest("IntradayBarRequest")
        End If
    
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = vtSecurity
            .Field = vtFields
            vtFields = ProcessFieldsArray(vtFields, True)
            .FieldMnemonic = vtFields
            .eventType = vtEvents
            .cookie = vtCookie
            .GMT = boolGMT
            .TimeOutMilliseconds = lngTimeOut
            .DisplayHorizontal = boolDisplayHorizontal
            .ReverseChronological = boolReverseChronological
            .ReturnProcedure = strRtnProc
            .MergeArrays = boolMergeResultArrays
            .StartDateTime = dtStartDate
            .EndDateTime = dtEndDate
            .Interval = lngInterval
            .FillType = Trim(strDefaultFillMethod)
            .NumberOfRequestPerSec = 1
            .SubRequests = GetTotalNonEmptySecurities(vtSecurity, vtEvents) * .NumberOfRequestPerSec
            .TheSameTimeFrameEveryDay = boolTheSameTimeFrameEveryDay
        End With
    
        Call objReq.Set("interval", CStr(lngInterval))
        
        
        If boolTheSameTimeFrameEveryDay Then
            Call objReq.GetElement("dateTimeInfo").SetChoice("startDateDuration")
            'duration = (dtEndDate - dtStartDate - Fix(dtEndDate - dtStartDate)) * 1440
            duration = (dtEndDate - dtStartDate - Fix(dtEndDate - dtStartDate)) * 1440 * 60
            Call objReq.GetElement("dateTimeInfo").GetElement("startDateDuration").GetElement("duration").SetValue(duration)
            Set objDateTimeDurations = objReq.GetElement("dateTimeInfo").GetElement("startDateDuration").GetElement("rangeStartDateTimeList")
            i = 0
            Do While dtStartDate + i < dtEndDate
                Call objDateTimeDurations.AppendValue(VBADateToBloombergDateTime(dtStartDate + i, boolGMT))
                i = i + 1
            Loop
        Else
            'Call objReq.GetElement("dateTimeInfo").SetChoice("dateTimeRange")
            Call objReq.GetElement("startDateTime").SetValue(VBADateToBloombergDateTime(dtStartDate, boolGMT))
            Call objReq.GetElement("endDateTime").SetValue(VBADateToBloombergDateTime(dtEndDate, boolGMT))
        End If
            
        
        If lngMaxDataPoints > 0 Then Call objReq.Set("maxDataPoints", CStr(lngMaxDataPoints))
    
        For i = LBound(vtBool) To UBound(vtBool)
            If IsMissing(vtBoolVal(i)) = False Then
                Call objReq.Set(CStr(vtBool(i)), CBool(vtBoolVal(i) = True))
            End If
        Next i
        
        lb = 0
        ub = 0
    
        
        For i = LBound(vtSecurity) To UBound(vtSecurity)
            If Trim(vtSecurity(i)) <> "" Then
                Call objReq.Set("security", CStr(vtSecurity(i)))
                For k = lb To ub
                    For j = LBound(vtEvents) To UBound(vtEvents)
                        If Trim(vtEvents(j)) <> "" Then
                            Call objReq.Set("eventType", CStr(vtEvents(j)))
                            Call SendRequest(objReq, objBlpReq, vtResult)
                        Else
                            m_count = m_count + 1
                        End If
                    Next j
                Next k
            Else
                m_count = ((m_count + UBound(vtEvents) - LBound(vtEvents) + 1)) * objBlpReq.NumberOfRequestPerSec
            End If
        Next i
    
    End If
        
    Set RequestIntradayBarData = objBlpReq

End Function

Public Function RequestIntradayTickData(ByVal vtSecurity As Variant, _
                                        ByRef vtCookie As Variant, _
                                        ByVal vtEvents As Variant, _
                                        ByVal vtFields As Variant, _
                                        ByRef dtStartDate As Date, _
                                        Optional ByVal dtEndDate As Date, _
                                        Optional ByRef vtIncludeNonPlottableEvents As Variant, _
                                        Optional ByRef lngMaxDataPoints As Long, _
                                        Optional ByRef boolReverseChronological As Boolean, _
                                        Optional ByRef boolDisplayHorizontal As Boolean, _
                                        Optional ByRef boolGMT As Boolean, _
                                        Optional ByRef strRtnProc As String, _
                                        Optional ByRef vtResult As Variant, _
                                        Optional ByRef lngTimeOut As Long, _
                                        Optional ByRef boolMergeResultArrays As Boolean = True, _
                                        Optional ByRef boolTheSameTimeFrameEveryDay = False, _
                                        Optional ByRef vtAdjustmentFollowDPDF As Variant, _
                                        Optional ByRef vtAdjustmentSplit As Variant, _
                                        Optional ByRef vtAdjustmentAbnormal As Variant, _
                                        Optional ByRef vtAdjustmentNormal As Variant) As clsBlpRequest



    'eventType: TRADE, BID, ASK, BID_BEST, ASK_BEST, BEST_BID, BEST_ASK, BID_YIELD, ASK_YIELD, MID_PRICE, AT_TRADE
    'fields: time, type, value, size, conditionCodes, exchangeCode, rpsCode, brokerBuyCode, brokerSellCode, micCode, "action", "indicator", "spreadPrice", "tradeTime","yield", upfrontPrice
    
    Dim i As Long, j As Long, k As Long
    Dim objReq As blpapicomLib2.REQUEST
    Dim objEvents As blpapicomLib2.element
    Dim objBlpReq As clsBlpRequest
    Dim vtBool As Variant, vtBoolVal As Variant
    Dim tmpStartTime As Double, tmpEndTime As Double
    
    Set objBlpReq = New clsBlpRequest

    If IniService(m_RefDataService, "//blp/refdata", objBlpReq) Then
    
        vtBool = Array("includeNonPlottableEvents", "includeConditionCodes", "includeExchangeCodes", "includeBrokerCodes", "includeRpsCodes", "includeBicMicCodes", "includeActionCodes", "includeIndicatorCodes", "includeSpreadPrice", "includeTradeTime", "includeYield", "includeUpfrontPrice", "adjustmentFollowDPDF", "adjustmentSplit", "adjustmentAbnormal", "adjustmentNormal")
        vtBoolVal = Array(vtIncludeNonPlottableEvents, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, vtAdjustmentFollowDPDF, vtAdjustmentSplit, vtAdjustmentAbnormal, vtAdjustmentNormal)
        
        If CDbl(dtEndDate) = 0 Then dtEndDate = Now
        
        Call ProcessArguments(vtSecurity, vtFields, vtEvents)
        
        Set objReq = m_RefDataService.CreateRequest("IntradayTickRequest")
        
        If boolTheSameTimeFrameEveryDay Then
            tmpStartTime = dtStartDate - Int(dtStartDate)
            tmpEndTime = dtEndDate - Int(dtEndDate)
            j = -CInt(tmpEndTime < tmpStartTime)
        End If
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = vtSecurity
            .Field = vtFields
            vtFields = ProcessFieldsArray(vtFields, True, vtBoolVal)
            .FieldMnemonic = vtFields
            .cookie = vtCookie
            .GMT = boolGMT
            .TimeOutMilliseconds = lngTimeOut
            .DisplayHorizontal = boolDisplayHorizontal
            .ReverseChronological = boolReverseChronological
            .ReturnProcedure = strRtnProc
            .MergeArrays = boolMergeResultArrays
    
            If boolTheSameTimeFrameEveryDay Then
                .NumberOfRequestPerSec = Int(dtEndDate) - Int(dtStartDate) + 1 - j
               .SubRequests = GetTotalNonEmptySecurities(vtSecurity) * .NumberOfRequestPerSec
            Else
                .NumberOfRequestPerSec = 1
              .SubRequests = GetTotalNonEmptySecurities(vtSecurity)
            End If
            .TheSameTimeFrameEveryDay = boolTheSameTimeFrameEveryDay
        End With
    
        If lngMaxDataPoints > 0 Then Call objReq.Set("maxDataPoints", CStr(lngMaxDataPoints))
    
        Set objEvents = objReq.GetElement("eventTypes")
        For k = LBound(vtEvents) To UBound(vtEvents)
            Call objEvents.AppendValue(UCase(vtEvents(k)))
        Next k
            
        For k = LBound(vtBool) To UBound(vtBool)
            If IsMissing(vtBoolVal(k)) = False Then
                Call objReq.Set(CStr(vtBool(k)), CBool(vtBoolVal(k) = True))
            End If
        Next k
        
        'We need to correctly set SubRequests before sending anyreuest. For future start days, we don't need to send anything
        If boolTheSameTimeFrameEveryDay Then
            For i = Int(dtStartDate) To Int(dtEndDate) - j
                If CDate(i + tmpStartTime) > Now Then
                    objBlpReq.SubRequests = objBlpReq.SubRequests - GetTotalNonEmptySecurities(vtSecurity)
                End If
            Next i
        End If
    
        For k = LBound(vtSecurity) To UBound(vtSecurity)
            If Trim(vtSecurity(k)) <> "" Then
                Call objReq.Set("security", CStr(vtSecurity(k)))
                If boolTheSameTimeFrameEveryDay Then
                    For i = Int(dtStartDate) To Int(dtEndDate) - j
                        If CDate(i + tmpStartTime) <= Now Then
                            Call objReq.Set("startDateTime", VBADateToBloombergDateTime(CDate(i + tmpStartTime), boolGMT))
                            Call objReq.Set("endDateTime", VBADateToBloombergDateTime(CDate(i + j + tmpEndTime), boolGMT))
                            Call SendRequest(objReq, objBlpReq, vtResult)
                        End If
                    Next i
                Else
                    Call objReq.Set("startDateTime", VBADateToBloombergDateTime(dtStartDate, boolGMT))
                    Call objReq.Set("endDateTime", VBADateToBloombergDateTime(dtEndDate, boolGMT))
                    Call SendRequest(objReq, objBlpReq, vtResult)
                End If
            Else
                m_count = m_count + 1
            End If
        Next k
    
        If Not IsMissing(vtResult) Then
            Call objBlpReq.FinalProcess
        End If
        
    End If
    
    Set RequestIntradayTickData = objBlpReq

End Function

Private Function ProcessFieldsArray(ByRef vtField As Variant, _
                                    ByRef boolIntraday As Boolean, _
                                    Optional ByRef vtBoolVal As Variant, _
                                    Optional ByRef vtUniqueFields As Variant) As Variant
    
    Dim j As Long
    Dim k As Long
    Dim v As Variant
    Dim objDic As Scripting.Dictionary
    
    If IsMissing(vtBoolVal) Then
        ReDim vtBoolVal(11) As Variant
    End If
    
    If IsArray(vtField) Then
        Set objDic = New Scripting.Dictionary
        ReDim v(LBound(vtField) To UBound(vtField)) As Variant
        ReDim vtUniqueFields(LBound(vtField) To UBound(vtField)) As Variant
        j = LBound(vtField)
        For k = LBound(vtField) To UBound(vtField)
            'Check LEN > 0 to avoid Empty being translated later to XX_TABLE_VERSION.
            If IsNumeric(vtField(k)) And Len(CStr(vtField(k))) > 0 Then
                v(k) = modValidation.xb_FieldMnemonic(CLng(vtField(k)))
            Else
                v(k) = vtField(k)
            End If
            Select Case LCase(Trim(v(k)))
                Case "date"
                    v(k) = "date"
                Case "relative date", "relative_date"
                    v(k) = "RELATIVE_DATE"
                    vtBoolVal(0) = True
                Case "data indicator", "data_indicator"
                    v(k) = "DATA_INDICATOR"
                    vtBoolVal(1) = True
                Case "time", "open", "high", "low", "close", "volume", "type", "value", "size"
                    If boolIntraday Then
                        v(k) = LCase(Trim(v(k)))
                    Else
                        v(k) = UCase(Trim(v(k)))
                    End If
                Case "numevents"
                    v(k) = "numEvents"
                Case "conditioncodes"
                    v(k) = "conditionCodes"
                    vtBoolVal(1) = True     'includeConditionCodes
                Case "exchangecode"
                    v(k) = "exchangeCode"
                    vtBoolVal(2) = True     'includeExchangeCodes
                Case "brokerbuycode"
                    v(k) = "brokerBuyCode"
                    vtBoolVal(3) = True     'includeBrokerCodes
                Case "brokersellcode"
                    v(k) = "brokerSellCode"
                    vtBoolVal(3) = True     'includeBrokerCodes
                Case "rpscode"
                    v(k) = "rpsCode"
                    vtBoolVal(4) = True     'includeRpsCodes
                Case "miccode"
                    v(k) = "micCode"
                    vtBoolVal(5) = True     'includeBicMicCodes
                Case "action"
                    v(k) = "action"
                    vtBoolVal(6) = True     'includeActionCodes
                Case "indicator"
                    v(k) = "indicator"
                    vtBoolVal(7) = True     'includeIndicatorCodes
                Case "spreadprice"
                    v(k) = "spreadPrice"
                    vtBoolVal(8) = True     'includeSpreadPrice
                Case "tradetime"
                    v(k) = "tradeTime"
                    vtBoolVal(9) = True     'includeTradeTime
                Case "yield"
                    v(k) = "yield"
                    vtBoolVal(10) = True    'includeYield
                Case "upfrontprice"
                    v(k) = "upfrontPrice"
                    vtBoolVal(11) = True    'includeUpfrontPrice
                Case Else
                    v(k) = Replace(UCase(Trim(v(k))), " ", "_")
            End Select
            If objDic.Exists(CStr(v(k))) = False Then
                Call objDic.Add(CStr(v(k)), v(k))
                vtUniqueFields(j) = v(k)
                j = j + 1
            End If
        Next k
    End If
    
    If j > 0 Then
        ReDim Preserve vtUniqueFields(j - 1) As Variant
    Else
        vtUniqueFields = Empty
    End If
    
    ProcessFieldsArray = v
        
End Function


Private Function HasValidOverrides(ByRef vtOvFields As Variant, ByRef vtOvValues As Variant, ByRef lngAdj As Long) As Boolean
    
    If IsMissing(vtOvFields) = False Then
        If IsMissing(vtOvValues) = False Then
            If IsArray(vtOvFields) = False Then vtOvFields = Array(vtOvFields)
            If IsArray(vtOvValues) = False Then vtOvValues = Array(vtOvValues)
            If UBound(vtOvFields) - LBound(vtOvFields) = UBound(vtOvValues) - LBound(vtOvValues) Then
                lngAdj = LBound(vtOvFields) - LBound(vtOvValues)
                HasValidOverrides = True
            End If
        End If
    End If
End Function

Private Function VBADateToBloombergDateTime(ByVal dt As Date, ByRef boolGMT As Boolean) As blpapicomLib2.DateTime

    Dim objDateTime As blpapicomLib2.DateTime
    
    If boolGMT = False Then dt = modUTC.LocalToUTC(dt)
    
    Set objDateTime = m_Session.CreateDatetime
    With objDateTime
        .Year = Year(dt)
        .Month = Month(dt)
        .Day = Day(dt)
        .Hour = Hour(dt)
        .Minute = Minute(dt)
        .Second = Second(dt)
    End With
    
    Set VBADateToBloombergDateTime = objDateTime
    
End Function

Public Function RequestHistoricalTAData(ByRef vtSecurity As Variant, _
                                        ByRef vtCookie As Variant, _
                                        ByRef vtFields As Variant, _
                                        ByRef strStdyName As String, _
                                        ByRef vtOptions As Variant, _
                                        ByRef vtOptionValues As Variant, _
                                        ByRef vtStartDate As Variant, _
                                        Optional ByVal vtEndDate As Variant, _
                                        Optional ByRef strCurrency As String, _
                                        Optional ByRef strPeriodicityAdjustment As String, _
                                        Optional ByRef strPeriodicitySelection As String, _
                                        Optional ByRef strNonTradingDayFillOption As String, _
                                        Optional ByRef strNonTradingDayFillMethod As String, _
                                        Optional ByRef strCalendarCodeOverride As String, _
                                        Optional ByRef strPricingOption As String, _
                                        Optional ByRef vtAdjustmentFollowDPDF As Variant, _
                                        Optional ByRef vtAdjustmentSplit As Variant, _
                                        Optional ByRef vtAdjustmentAbnormal As Variant, _
                                        Optional ByRef vtAdjustmentNormal As Variant, _
                                        Optional ByRef boolReverseChronological As Boolean, _
                                        Optional ByRef boolDisplayHorizontal As Boolean, _
                                        Optional ByRef boolConvertDatesTorStringBefore1900 As Boolean, _
                                        Optional ByRef strRtnProc As String, _
                                        Optional ByRef vtResult As Variant, Optional ByRef lngTimeOut As Long, _
                                        Optional ByRef boolMergeResultArrays As Boolean = True, Optional ByRef numDataPoints As Long) As clsBlpRequest
                                            
                                            
    Dim k As Long
    Dim objReq As blpapicomLib2.REQUEST  'LG
    Dim objBlpReq As clsBlpRequest
    Dim strError As String
    
    Dim vtString As Variant, vtStringVal As Variant, vtBool As Variant, vtBoolVal As Variant
    
    'periodicityAdjustment:     ACTUAL, CALENDAR, FISCAL
    'periodicitySelection :     DAILY, WEEKLY, MONTHLY, QUARTERLY, SEMI_ANNUALLY, YEARLY
    'overrideOption:            OVERRIDE_OPTION_CLOSE, OVERRIDE_OPTION_GPA
    'pricingOption :            PRICING_OPTION_PRICE, PRICING_OPTION_YIELD
    'nonTradingDayFillOption:   NON_TRADING_WEEKDAYS, ALL_CALENDAR_DAYS , ACTIVE_DAYS_ONLY
    'nonTradingDayFillMethod:   PREVIOUS_VALUE, NIL_VALUE
       
    Set objBlpReq = New clsBlpRequest
        
    If IniService(m_TADataService, "//blp/tasvc", objBlpReq) Then
    
        vtString = Array("currency", "periodicityAdjustment", "periodicitySelection", "nonTradingDayFillOption", "nonTradingDayFillMethod", "calendarCodeOverride", "pricingOption")
        vtStringVal = Array(strCurrency, strPeriodicityAdjustment, strPeriodicitySelection, strNonTradingDayFillOption, strNonTradingDayFillMethod, strCalendarCodeOverride, strPricingOption)
        vtBool = Array("adjustmentFollowDPDF", "adjustmentSplit", "adjustmentAbnormal", "adjustmentNormal")
        vtBoolVal = Array(vtAdjustmentFollowDPDF, vtAdjustmentSplit, vtAdjustmentAbnormal, vtAdjustmentNormal)
        
        Call ProcessArguments(vtSecurity, vtFields, vtOptions, vtOptionValues)
        'If IsArray(vtSecurity) = False Then vtSecurity = Array(vtSecurity)
        If IsDate(vtStartDate) Then vtStartDate = Format(CDate(vtStartDate), "YYYYMMDD")
        If IsMissing(vtEndDate) Then vtEndDate = Date
        If IsDate(vtEndDate) Then vtEndDate = Format(CDate(vtEndDate), "YYYYMMDD")
    
        Set objReq = m_TADataService.CreateRequest("studyRequest")
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = vtSecurity
            .Field = vtFields
            .FieldMnemonic = vtFields
            .TAStudyName = strStdyName
            .cookie = vtCookie
            .ConvertDatesTorStringBefore1900 = boolConvertDatesTorStringBefore1900
            .DisplayHorizontal = boolDisplayHorizontal
            .ReverseChronological = boolReverseChronological
            .TimeOutMilliseconds = lngTimeOut
            .ReturnProcedure = strRtnProc
            .MergeArrays = boolMergeResultArrays
            .numDataPoints = numDataPoints
            .SubRequests = GetTotalNonEmptySecurities(vtSecurity)
            'Call m_Requests.Add(objBlpReq, CStr(m_Count))
        End With
            
        Call objReq.GetElement("priceSource").GetElement("dataRange").SetChoice("historical")
        Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("historical").GetElement("startDate").SetValue(CStr(vtStartDate))
        Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("historical").GetElement("endDate").SetValue(CStr(vtEndDate))
            
        For k = LBound(vtStringVal) To UBound(vtStringVal)
            If CStr(vtStringVal(k)) <> "" Then
                Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("historical").GetElement(CStr(vtString(k))).SetValue(CStr(vtStringVal(k)))
            End If
        Next k
        
        For k = LBound(vtBoolVal) To UBound(vtBoolVal)
            If IsMissing(vtBoolVal(k)) = False Then
                Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("historical").GetElement(CStr(vtBool(k))).SetValue(CStr(vtBoolVal(k)))
            End If
        Next k
    '    Set prepareHistoricalTARequest = objReq
        
        If prepareTAnameAndPara(objReq, strStdyName, vtOptions, vtOptionValues, strError) Then
            For k = LBound(vtSecurity) To UBound(vtSecurity)
                If Trim(vtSecurity(k)) <> "" Then
                    Call objReq.GetElement("priceSource").GetElement("securityName").SetValue(CStr(vtSecurity(k)))
                    Call SendRequest(objReq, objBlpReq, vtResult)
                Else
                    m_count = m_count + 1
                End If
            Next k
        Else
            objBlpReq.Error = strError
        End If
    
    End If
    
    Set RequestHistoricalTAData = objBlpReq
       
End Function

Public Function RequestIntradayTABarData(ByRef vtSecurity As Variant, _
                                         ByRef vtCookie As Variant, _
                                         ByVal vtEvents As Variant, _
                                         ByVal vtFields As Variant, _
                                         ByRef strStdyName As String, _
                                         ByRef vtOptions As Variant, _
                                         ByRef vtOptionValues As Variant, _
                                         ByRef dtStartDate As Date, _
                                         Optional ByVal dtEndDate As Date, _
                                         Optional ByVal lngInterval As Long, _
                                         Optional ByRef vtFillInitialBar As Variant, _
                                         Optional ByRef vtAdjustmentFollowDPDF As Variant, _
                                         Optional ByRef vtAdjustmentSplit As Variant, _
                                         Optional ByRef vtAdjustmentAbnormal As Variant, _
                                         Optional ByRef vtAdjustmentNormal As Variant, _
                                         Optional ByRef boolReverseChronological As Boolean, _
                                         Optional ByRef boolDisplayHorizontal As Boolean, _
                                         Optional ByRef boolGMT As Boolean, _
                                         Optional ByRef strRtnProc As String, _
                                         Optional ByRef vtResult As Variant, _
                                         Optional ByRef lngTimeOut As Long, _
                                         Optional ByRef boolMergeResultArrays As Boolean = True) As clsBlpRequest
                                            
    '--------------------------------------------------------------------
    ' Function: RequestIntradayTABarData
    ' Module:   clsBlpApi
    ' Author:
    ' Date:
    ' Purpose:  Requests intraday technical analysis bar data
    '
    ' Returns: Instance of clsBlpRequest
    '
    ' Parameters:
    '   vtSecurity              (i): A string or variant containing the ticker id(s) for which data is being requested.
    '   vtCookie                (i): Cookie (ID) for the request.
    '   vtEvents                (i): The events(s) being requested.
    '                                eventTypes: TRADE , BID, ASK, BID_BEST, ASK_BEST, BID_YIELD, ASK_YIELD, MID_PRICE, AT_TRADE, BEST_BID, BEST_ASK
    '   vtFields                (i): The output field(s) being requested - specific to the technical study being requested e.g. for MAE: "Date, MAE_UPPER, MAE_LOWER"
    '   strStdyName             (i): The identifier (abbreviation) for the requested technical study e.g. DMI, RSI, SMAVG, MAE etc
    '   vtOptions               (i): Input argument names. May be specific to requested study.e.g. No of periods, upper limit, lower limit
    '   vtOptionValues          (i): Input argument values for the corresponding arguments above.
    '   dtStartDate             (i): Start Date
    '   dtEndDate               (i): End Date
    '   lngInterval             (i): Bar Size in Minutes (>=1)
    '   vtFillInitialBar        (i): Indicates whether to always get the initial bar for "Previous" fill
    '   vtAdjustmentFollowDPDF  (i): Follows DPDF settings
    '   vtAdjustmentSplit       (i): DPDF settings, Whether to use pricing defaults for distributions. All other options are ignored.
    '   vtAdjustmentAbnormal    (i): DPDF settings, Cash Adjustment Abnormal.
    '                                Adjust to reflect: Special Cash, Liquidation, Capital Gains,
    '                                Long-Term Capital Gains, Short-Term Capital Gains, Memorial,
    '                                Return of Capital, Rights Redemption, Miscellaneous, Return Premium,
    '                                Preferred Rights Redemption, Proceeds/Rights, Proceeds/Shares, Proceeds/Warrants.
    '   vtAdjustmentNormal      (i): DPDF settings, Cash Adjustment Normal.
    '                                Adjust  to reflect: Regular Cash, Interim, 1st Interim, 2nd Interim, 3rd Interim,
    '                                4th Interim, 5th Interim, Income, Estimated, Partnership Distribution, Final,
    '                                Interest on Capital, Distribution, Prorated.
    '   boolReverseChronological(i): TRUE will output newer data first
    '   boolDisplayHorizontal   (i): TRUE will arrange the data horizontally
    '   boolGMT                 (i): TRUE will consider input dates and times as GMT
    '   strRtnProc              (i): Use this paramater if you want to force a return procedure to use
    '   vtResult                (i): If empty, the procedure will be asynchronous.
    '                                If not, this variant will contain the data returned
    '   lngTimeOut              (i): If procedure is asynchronous, define the timeout (in milliseconds)
    '   boolMergeResultArrays   (i): Merge results in a single array
    
    '
    ' Last updated: 2014/01/28
    ' By:           jhall
    '------------------------------------------------------------------
    
    
    Dim i As Long, j As Long
    Dim objReq As blpapicomLib2.REQUEST 'LG
    Dim objBlpReq As clsBlpRequest
    Dim vtBool As Variant, vtBoolVal As Variant
    Dim strError As String
        
    Set objBlpReq = New clsBlpRequest
    
    If IniService(m_TADataService, "//blp/tasvc", objBlpReq) Then
    
        vtBool = Array("gapFillInitialBar", "adjustmentFollowDPDF", "adjustmentSplit", "adjustmentAbnormal", "adjustmentNormal")
        vtBoolVal = Array(vtFillInitialBar, vtAdjustmentFollowDPDF, vtAdjustmentSplit, vtAdjustmentAbnormal, vtAdjustmentNormal)
        
        If lngInterval < 1 Then lngInterval = 1
        If CDbl(dtEndDate) = 0 Then dtEndDate = Now
        
        Call ProcessArguments(vtSecurity, vtFields, vtEvents, vtOptions, vtOptionValues)

        Set objReq = m_TADataService.CreateRequest("studyRequest")
        
        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = vtSecurity
            .Field = vtFields
    '        vtFields = ProcessFieldsArray(vtFields, True, vtBoolVal)
            .FieldMnemonic = vtFields
            .eventType = vtEvents
            .cookie = vtCookie
            .GMT = boolGMT
            .TimeOutMilliseconds = lngTimeOut
            .DisplayHorizontal = boolDisplayHorizontal
            .ReverseChronological = boolReverseChronological
            .ReturnProcedure = strRtnProc
            .MergeArrays = boolMergeResultArrays
            .SubRequests = GetTotalNonEmptySecurities(vtSecurity, vtEvents)
        End With
        
        Call objReq.GetElement("priceSource").GetElement("dataRange").SetChoice("intraday")
        Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("intraday").GetElement("startDate").SetValue(VBADateToBloombergDateTime(dtStartDate, boolGMT))
        Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("intraday").GetElement("endDate").SetValue(VBADateToBloombergDateTime(dtEndDate, boolGMT))
        Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("intraday").GetElement("interval").SetValue(CStr(lngInterval))
        
        For i = LBound(vtBoolVal) To UBound(vtBoolVal)
            If IsMissing(vtBoolVal(i)) = False Then
                Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("intraday").GetElement(CStr(vtBool(i))).SetValue(CBool(vtBoolVal(i) = True))
            End If
        Next i
        
        If prepareTAnameAndPara(objReq, strStdyName, vtOptions, vtOptionValues, strError) Then
            For i = LBound(vtSecurity) To UBound(vtSecurity)
                If Trim(vtSecurity(i)) <> "" Then
                    Call objReq.GetElement("priceSource").GetElement("securityName").SetValue(CStr(vtSecurity(i)))
                    For j = LBound(vtEvents) To UBound(vtEvents)
                        If Trim(vtEvents(j)) <> "" Then
                            Call objReq.GetElement("priceSource").GetElement("dataRange").GetElement("intraday").GetElement("eventType").SetValue(CStr(vtEvents(j)))
                            Call SendRequest(objReq, objBlpReq, vtResult)
                        Else
                            m_count = m_count + 1
                        End If
                    Next j
                Else
                    m_count = m_count + UBound(vtEvents) - LBound(vtEvents) + 1
                End If
            Next i
        Else
            objBlpReq.Error = strError
        End If
    
    End If
    
    Set RequestIntradayTABarData = objBlpReq
       
End Function

Private Function prepareTAnameAndPara(ByRef objReq As blpapicomLib2.REQUEST, ByRef stdyName As String, ByVal options As Variant, ByVal optionValues As Variant, ByRef strError As String) As Boolean
    
    Dim b As Boolean
    Dim i As Long, j As Long
    '7/19/2011-XB: beaking down objects to ensure Study object gets properly created
    Dim objStudyAttributes As blpapicomLib2.element
    Dim objStudy As blpapicomLib2.element
    Dim objOption As blpapicomLib2.element
        
    stdyName = Trim(stdyName)
    
    If IsArray(options) = False Then options = Array(options)
    If IsArray(optionValues) = False Then optionValues = Array(optionValues)
    
    If UBound(options) - LBound(options) = UBound(optionValues) - LBound(optionValues) Then
        
        j = LBound(options) - LBound(optionValues)
        
        If stdyName <> "" Then
                        
            On Error Resume Next
            Set objStudyAttributes = objReq.GetElement("studyAttributes")
            
            Call objStudyAttributes.SetChoice(stdyName)
            
            If objStudyAttributes.HasElement(stdyName) Then
                
                Set objStudy = objReq.GetElement("studyAttributes").GetElement(stdyName)
                
                If Not (objStudy Is Nothing) Then
                    b = True
                    strError = ""
                    For i = LBound(options) To UBound(options)
                        Set objOption = objStudy.GetElement(Trim(options(i)))
                        Call objOption.SetValue(ModifyParameter(optionValues(i - j), False, False)) 'CStr(optionValues(i - j)))
                        If Err.Number <> 0 Then
                            b = False
                            strError = Err.Description
                            Exit For
                        End If
                    Next i
                End If

            Else
                strError = Err.Description
            End If
            
            On Error GoTo 0
            
        End If
    Else
        strError = "Different number of study parameter names and values."
    End If
    
   prepareTAnameAndPara = b
   
End Function

Private Function GetTotalNonEmptySecurities(ByRef vtSecurity As Variant, Optional ByVal vtEvents As Variant) As Long
   Dim k As Long, total As Long
   
   total = 0
   For k = LBound(vtSecurity) To UBound(vtSecurity)
            If Trim(vtSecurity(k)) <> "" Then
                total = total + GetTotalVtEvents(vtEvents)
            End If
   Next k

   GetTotalNonEmptySecurities = total

End Function

Private Function GetTotalVtEvents(Optional ByVal vtEvents As Variant) As Long
   Dim total As Long
   Dim j As Long
   total = 0
   
   If (IsMissing(vtEvents)) Then
       GetTotalVtEvents = 1
       Exit Function
   End If
   
   
   For j = LBound(vtEvents) To UBound(vtEvents)
       If Trim(vtEvents(j)) <> "" Then
             total = total + 1
       End If
  Next j

  GetTotalVtEvents = total
End Function

Private Function SendRequest(ByRef objReq As blpapicomLib2.REQUEST, ByRef objBlpReq As clsBlpRequest, ByRef vtResult As Variant, Optional ByRef isFakeRequest As Boolean) As Boolean
    
    Dim objCid As blpapicomLib2.CorrelationId
    Dim objQueue As blpapicomLib2.EventQueue
    Dim objEvent As blpapicomLib2.Event
    Dim b As Boolean ', boolType As Boolean
    Dim dt As Date
    Dim l As Long
    
    If Initialized Then
    
        Set objQueue = m_Session.CreateEventQueue
        
        'XB: 2012-04-17 Facing an issue. Temporary fix...
'        Do Until IsInCollection(m_Requests, CStr(m_Count)) = False
'            m_Count = m_Count + 1
'        Loop
        
        Set objCid = m_Session.CreateCorrelationId(m_count)
        
        If objBlpReq.id = BLPREQUEST_ID_NON_INITIALIZED Then
            objBlpReq.id = m_count
        End If
        objBlpReq.ID2 = m_count
        
        'objBlpReq.SubRequests = objBlpReq.SubRequests + 1
        Call m_Requests.Add(objBlpReq, CStr(objCid.Value))
        
        'XB: 2012-04-19 Moving this line up from the bottom of the module.
        m_count = m_count + 1

        'LG:2011/08/12: vtResult is missing --> Asynchronous treatment
        If IsMissing(vtResult) Then
            If Trim(objBlpReq.ReturnProcedure) = "" Then objBlpReq.ReturnProcedure = m_DataProcedure
'            Select Case objReq.AsElement.Name
'                Case "ReferenceDataRequest"
'                    boolType = True
'            End Select
'            If boolType And ((objReq.GetElement("securities").count = 0) Or (objReq.GetElement("fields").count = 0)) Then
'                m_EventsExpected = m_EventsExpected + 1
'                m_FakeEventCID = CStr(objCid.value)
'                Call m_Session_ProcessEvent(Nothing)
'            Else
            If Not isFakeRequest Then
                Set objCid = m_Session.SendRequest(objReq, objCid)
                m_EventsExpected = m_EventsExpected + 1
            Else
                m_EventsExpected = m_EventsExpected + 1
                m_FakeEventCID = CStr(objCid.Value)
                Call m_Session_ProcessEvent(Nothing)
            End If
            
        ElseIf Not isFakeRequest Then
            
            'LG:2011/08/12: vtResult is present --> Synchronous treatment
            Set objCid = m_Session.SendRequest(objReq, objCid, objQueue)
            m_EventsExpected = m_EventsExpected + 1
             
            l = objBlpReq.TimeOutMilliseconds
            If l <= 0 Then l = m_TimeOutMilliseconds
                    
            objBlpReq.Synchronous = True
            dt = Now
            
            Do Until b
                If Now > dt + l / 86400000 Then
                    objBlpReq.TimeOut = True
                    Exit Do
                End If
                Set objEvent = objQueue.NextEvent(l)
                On Error Resume Next
                b = CBool(objEvent.eventType = 5)
                If Err.Number = 0 Then Call m_Session_ProcessEvent(objEvent)
                On Error GoTo 0
                If m_DoEvents Then DoEvents
            Loop
            
            vtResult = objBlpReq.Data
            
        Else
            objBlpReq.Synchronous = True
            m_FakeEventCID = CStr(objCid.Value)
            Call m_Session_ProcessEvent(Nothing)
            vtResult = objBlpReq.Data
        End If
        'XB: 2012-04-19 Moving this line up from the bottom of the module.
        'm_Count = m_Count + 1
        
        SendRequest = True
        
    End If

End Function

Private Sub worksAfterProcessedBloombergData(objBlpReq As clsBlpRequest, eventType As Long)
    Dim k As Long
    Dim dblProgress As Double
    'If objBlpReq.Synchronous = False Then
        m_EventsReceived = m_EventsReceived + 1
        m_EventsExpected = m_EventsExpected - CBool(eventType = 6)
        If m_EventsExpected <> 0 Then dblProgress = m_EventsReceived / m_EventsExpected
        RaiseEvent Progress(dblProgress, objBlpReq.Complete)
        If m_ProgressProcedure <> "" Then
            On Error Resume Next
            Call Application.Run(m_ProgressProcedure, dblProgress, objBlpReq.Complete)
            On Error GoTo 0
        End If
    'End If
    If objBlpReq.Complete Then
        If objBlpReq.Synchronous = False Then
            RaiseEvent Data(objBlpReq)
            If Trim(objBlpReq.ReturnProcedure) = "" Then objBlpReq.ReturnProcedure = m_DataProcedure
            If objBlpReq.ReturnProcedure <> "" Then
                On Error Resume Next
                Call Application.Run(objBlpReq.ReturnProcedure, objBlpReq)
                On Error GoTo 0
            End If
        End If
        If m_KeepData = False Then
            'Handling the case where results were sent back several times
            On Error Resume Next
            For k = objBlpReq.ID2 To objBlpReq.id Step -1
                If IsInCollection(m_Requests, CStr(k)) Then
                    Call m_Requests.Remove(CStr(k))
                End If
            Next k
            On Error GoTo 0
        End If
        If m_EventsReceived = m_EventsExpected Then
            m_EventsReceived = 0
            m_EventsExpected = 0
        End If
    End If

End Sub
 
Private Sub m_Session_ProcessEvent(ByVal obj As Object)

    Dim objDic As Scripting.Dictionary
    Dim EventObj As blpapicomLib2.Event 'LG
    Dim it As blpapicomLib2.MessageIterator
    Dim msg As blpapicomLib2.Message
    Dim objElement As blpapicomLib2.element
    Dim objBlpReq As New clsBlpRequest
    Dim k As Long
    Dim s As String, strError As String
    
    Dim strStatus As String
        
    If obj Is Nothing Then
        If IsInCollection(m_Requests, m_FakeEventCID) Then
            Set objBlpReq = m_Requests.Item(m_FakeEventCID)
            Call objBlpReq.ProcessBloombergData(Nothing, True, CLng(m_FakeEventCID))
            Call worksAfterProcessedBloombergData(objBlpReq, response)
        End If
    ElseIf VarType(obj) = 9 Then
    
        If TypeName(obj) = "Event" Then
        
            strError = "responseError"
            Set EventObj = obj
            On Error Resume Next
            k = EventObj.eventType
            On Error GoTo 0
            
            Set it = EventObj.CreateMessageIterator()
            
            Do While it.Next()
                
                Set msg = it.Message
                
                If m_SaveDataLog Then
                    On Error Resume Next
                    Open ThisWorkbook.Path & "\clsBlpApi.log" For Append As #1
                        Print #1, Format(Now, "dd-mmm-yyyy hh:mm:ss") & ": " & msg.MessageTypeAsString
                        Print #1, msg.Print
                        Print #1, vbCrLf
                    Close #1
                    On Error GoTo 0
                End If
                    
                Select Case k
                    Case SUBSCRIPTION_DATA      'Subscription Data
                    
                        If msg.CorrelationId.Value = -1234567890 Then   'FXAPI subscriptions
                            
                            If IsInCollection(m_Requests, CStr(msg.CorrelationId.Value)) Then
                            
                                Set objBlpReq = m_Requests.Item(CStr(msg.CorrelationId.Value))
                                Set objDic = objBlpReq.FXAPIMessageToDictionary(msg)
                            
                                RaiseEvent FXAPISubscription(objDic)
                                If m_FXAPISubscriptionProcedure <> "" Then
                                    On Error Resume Next
                                    Call Application.Run(m_FXAPISubscriptionProcedure, objDic)
                                    On Error GoTo 0
                                End If
                            
                            End If
                            
                        Else
                            
                            If IsInCollection(m_Requests, "sub" & CStr(msg.CorrelationId.Value)) Then
                                Set objBlpReq = m_Requests.Item("sub" & CStr(msg.CorrelationId.Value))
                                s = CallByName(msg, "MessageTypeAsString", VbGet)
                                If objBlpReq.ProcessBloombergData(msg.AsElement, True, msg.CorrelationId.Value) Then
                                    RaiseEvent SubscriptionData(objBlpReq)
                                    If m_SubscriptionProcedure <> "" Then
                                        On Error Resume Next
                                        Call Application.Run(m_SubscriptionProcedure, objBlpReq)
                                        On Error GoTo 0
                                    End If
                                End If
                            End If
                            
                        End If
                        
                    Case response, PARTIAL_RESPONSE   'Response, Partial Response
                        If IsInCollection(m_Requests, CStr(msg.CorrelationId.Value)) Then
                            Set objBlpReq = m_Requests.Item(CStr(msg.CorrelationId.Value))
                            Select Case objBlpReq.requestType
                                Case "studyRequest"
                                    s = "studyData"
                                    strError = "studyError"
                                Case "IntradayBarRequest", "IntradayBarDateTimeChoiceRequest"
                                    s = "barData"
                                Case "IntradayTickRequest"
                                    s = "tickData"
                                Case "BeqsRequest"
                                    s = "data"
                                Case "fieldInfoRequest"
                                    s = "fieldData"
                                Case "curveListRequest", "govtListRequest", "instrumentListRequest"
                                    s = "results"
                                Case "ExcelGetGridRequest"
                                    s = "DataRecords"
                                Case "SnapshotRequest"
                                    s = "snapshot"
                                Case "sendSheet", "sendEpsSheet"
                                    s = "rcode"
                                Case Else
                                    s = "securityData"
                            End Select
                            
                            If msg.AsElement.HasElement(strError) Then
                                Call objBlpReq.ProcessBloombergData(msg.GetElement(strError), CBool(k = 5), CLng(msg.CorrelationId.Value))
                            ElseIf msg.AsElement.HasElement(s) Then
                                If s = "DataRecords" Then
                                    Set objElement = msg.AsElement
                                Else
                                    Set objElement = msg.GetElement(s)
                                End If
                                Call objBlpReq.ProcessBloombergData(objElement, CBool(k = 5), CLng(msg.CorrelationId.Value))
                            End If
                            Call worksAfterProcessedBloombergData(objBlpReq, k)
                        End If
                        
                
                    Case SESSION_STATUS 'Session Status
                        m_SessionState = msg.MessageTypeAsString
                        Call ProcessStatusEvent(msg.MessageTypeAsString)
                        
                    Case BLPSERVICE_STATUS 'Service Status
                        Call ProcessStatusEvent(msg.MessageTypeAsString)
                        
                    Case SUBSCRIPTION_STATUS 'Service Status
                        Call ProcessStatusEvent(msg.MessageTypeAsString)
                        
                    Case Else
                        Call ProcessStatusEvent(msg.MessageTypeAsString)
    
        
                End Select
                
            Loop
        
        End If
        
    End If

End Sub

#If EnableManagedTick Then
Public Function RequestManagedTickData(ByRef requestSetting As clsTickRequestSetting, Optional vtResult As Variant) As clsBlpRequest

    'eventType: TRADE, BID, ASK, BID_BEST, ASK_BEST, BEST_BID, BEST_ASK, BID_YIELD, ASK_YIELD, MID_PRICE, AT_TRADE
    'fields: time, type, value, size, conditionCodes, exchangeCode, rpsCode, brokerBuyCode, brokerSellCode, micCode, "action", "indicator", "spreadPrice", "tradeTime","yield", upfrontPrice
    
    Dim i As Long, j As Long, k As Long
    Dim objReq As blpapicomLib2.REQUEST
    Dim objEvents As blpapicomLib2.element
    Dim objBlpReq As clsBlpRequest
    Dim vtBool As Variant, vtBoolVal As Variant
    Dim tmpStartTime As Double, tmpEndTime As Double
    Dim vtSecurity As Variant
    Dim sec As clsSecurity
    
    
    Set objBlpReq = New clsBlpRequest
    
    If Not requestSetting.isValidRequest() Then
        objBlpReq.Error = "Required Field is not passed"
        Exit Function
    End If
    vtSecurity = requestSetting.getSecurityListAsStringArray()

    If IniService(m_RefDataService, "//blp/refdata", objBlpReq) Then
    
        vtBool = Array("includeNonPlottableEvents", "includeConditionCodes", "includeExchangeCodes", "includeBrokerCodes", "includeRpsCodes", "includeBicMicCodes", "includeActionCodes", "includeIndicatorCodes", "includeSpreadPrice", "includeTradeTime", "includeYield", "includeUpfrontPrice")
        vtBoolVal = Array(requestSetting.vtIncludeNonPlottableEvents, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty)
        

        If CDbl(requestSetting.dtEndDate) = 0 Then requestSetting.dtEndDate = Now

        Call ProcessArguments(requestSetting.vtFields, requestSetting.vtEvents)
        
        Set objReq = m_RefDataService.CreateRequest("IntradayTickRequest")

        If requestSetting.boolTheSameTimeFrameEveryDay Then
            tmpStartTime = requestSetting.dtStartDate - Int(requestSetting.dtStartDate)
            tmpEndTime = requestSetting.dtEndDate - Int(requestSetting.dtEndDate)
            j = -CInt(tmpEndTime < tmpStartTime)
        End If

        With objBlpReq
            .id = BLPREQUEST_ID_NON_INITIALIZED
            .requestType = objReq.AsElement.Name
            .security = vtSecurity
            .Field = requestSetting.vtFields
            requestSetting.vtFields = ProcessFieldsArray(requestSetting.vtFields, True, vtBoolVal)
            .FieldMnemonic = requestSetting.vtFields
            .cookie = requestSetting.vtCookie
            .GMT = requestSetting.boolGMT
            .TimeOutMilliseconds = requestSetting.lngTimeOut
            .DisplayHorizontal = False
            .ReturnProcedure = requestSetting.strRtnProc
            .isManaged = True
            .requestBeginTime = Timer
            Set .managedRequestSetting = requestSetting

            
            If requestSetting.boolTheSameTimeFrameEveryDay Then
                .NumberOfRequestPerSec = Int(requestSetting.dtEndDate) - Int(requestSetting.dtStartDate) + 1 - j
               .SubRequests = GetTotalNonEmptySecurities(vtSecurity) * .NumberOfRequestPerSec
            Else
                .NumberOfRequestPerSec = 1
              .SubRequests = GetTotalNonEmptySecurities(vtSecurity)
            End If
            .TheSameTimeFrameEveryDay = requestSetting.boolTheSameTimeFrameEveryDay
            
        End With

        Set objEvents = objReq.GetElement("eventTypes")
        For k = LBound(requestSetting.vtEvents) To UBound(requestSetting.vtEvents)
            Call objEvents.AppendValue(UCase(requestSetting.vtEvents(k)))
        Next k

        For k = LBound(vtBool) To UBound(vtBool)
            If IsMissing(vtBoolVal(k)) = False Then
                Call objReq.Set(CStr(vtBool(k)), CBool(vtBoolVal(k) = True))
            End If
        Next k

        'We need to correctly set SubRequests before sending anyreuest. For future start days, we don't need to send anything
        If requestSetting.boolTheSameTimeFrameEveryDay Then
            For i = Int(requestSetting.dtStartDate) To Int(requestSetting.dtEndDate) - j
                If CDate(i + tmpStartTime) > Now Then
                    objBlpReq.SubRequests = objBlpReq.SubRequests - GetTotalNonEmptySecurities(vtSecurity)
                End If
            Next i
        End If

        For k = LBound(vtSecurity) To UBound(vtSecurity)
            'If requestSetting.lngMaxDataPoints > 0 Then Call objReq.Set("maxDataPoints", CStr(requestSetting.lngMaxDataPoints))
            If Trim(vtSecurity(k)) <> "" Then
                Set sec = requestSetting.getSecurityObject(vtSecurity(k))
                Call objReq.Set("maxDataPoints", CStr(sec.MaxNumberOfTicks))
                
                Call objReq.Set("security", CStr(vtSecurity(k)))
                If requestSetting.boolTheSameTimeFrameEveryDay Then
                    For i = Int(requestSetting.dtStartDate) To Int(requestSetting.dtEndDate) - j
                        If CDate(i + tmpStartTime) <= Now Then
                            Call objReq.Set("startDateTime", VBADateToBloombergDateTime(CDate(i + tmpStartTime), requestSetting.boolGMT))
                            Call objReq.Set("endDateTime", VBADateToBloombergDateTime(CDate(i + j + tmpEndTime), requestSetting.boolGMT))
                            Call SendRequest(objReq, objBlpReq, vtResult)
                        End If
                    Next i
                Else
                    Call objReq.Set("startDateTime", VBADateToBloombergDateTime(requestSetting.dtStartDate, requestSetting.boolGMT))
                    Call objReq.Set("endDateTime", VBADateToBloombergDateTime(requestSetting.dtEndDate, requestSetting.boolGMT))
                    Call SendRequest(objReq, objBlpReq, vtResult)
                End If
            Else
                m_count = m_count + 1
            End If
        Next k
        
    End If

    Set RequestManagedTickData = objBlpReq

End Function
#End If

Private Sub ProcessStatusEvent(ByRef strMessage As String)
    RaiseEvent Status(strMessage)
    If m_StatusProcedure <> "" Then
        On Error Resume Next
        Call Application.Run(m_StatusProcedure, strMessage)
        On Error GoTo 0
    End If
End Sub




