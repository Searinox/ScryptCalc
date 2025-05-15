import base64,ctypes,gc,hashlib,keyboard,os,sys,threading,time
from PyQt5.QtCore import (PYQT_VERSION_STR,Qt,QObject,QCoreApplication,QByteArray,pyqtSignal,qInstallMessageHandler,QTimer)
from PyQt5.QtWidgets import (QApplication,QMenu,QLabel,QLineEdit,QMainWindow,QPushButton,QSpinBox,QPlainTextEdit,QComboBox,QCheckBox)
from PyQt5.QtGui import (QFont,QPixmap,QImage,QIcon,QTextOption,QTextCursor,QCursor,QKeySequence)

gc_lock=threading.Lock()

def Cleanup_Memory():
    gc_lock.acquire()
    gc.collect()
    gc_lock.release()
    return

gc.enable()
gc.set_threshold(1,1,1)

GetTickCount64=ctypes.windll.kernel32.GetTickCount64
GetTickCount64.restype=ctypes.c_uint64
GetTickCount64.argtypes=()

PYQT5_MAX_SUPPORTED_COMPILE_VERSION="5.12.2"

def Versions_Str_Equal_Or_Less(version_expected,version_actual):
    version_compliant=False
    compared_versions=[]
    for compared_version in [version_expected,version_actual]:
        compared_versions+=[[int(number.strip()) for number in compared_version.split(".")]]
    if compared_versions[1][0]<=compared_versions[0][0]:
        if compared_versions[1][0]<compared_versions[0][0]:
            version_compliant=True
        elif compared_versions[1][1]<=compared_versions[0][1]:
            if compared_versions[1][1]<compared_versions[0][1]:
                version_compliant=True
            elif compared_versions[1][2]<=compared_versions[0][2]:
                version_compliant=True
    return version_compliant

def Get_Config_String_From_File(input_file_path):
    try:
        with open(input_file_path,"r") as file_handle:
            file_handle.seek(0,2)
            file_size=file_handle.tell()
            file_handle.seek(0,0)
            if file_size<=768:
                config_string=file_handle.read()
            else:
                config_string=u""
            config_string=str(config_string)
    except:
        config_string=u""
    
    return config_string


class ScryptCalc(object):
    APP_ICON_BASE64=b"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"
    
    MAINTHREAD_HEARTBEAT_SECONDS=0.1
    PENDING_ACTIVITY_HEARTBEAT_SECONDS=0.1
    ALTERNATE_PASTE_INTERKEY_DELAY_SECONDS=0.017
    CLIPBOARD_SET_TIMEOUT_MILLISECONDS=1000

    COMPUTE_MEMORY_MAX_BYTES=1024**3*2-1

    PARAM_TITLE_LENGTH_MAX=24
    PARAM_INPUT_MAX=192
    PARAM_SALT_MAX=192
    PARAM_N_EXPONENT_MIN=1
    PARAM_N_EXPONENT_MAX=22
    PARAM_R_MIN=1
    PARAM_R_MAX=128
    PARAM_P_MIN=1
    PARAM_P_MAX=192
    PARAM_LENGTH_MAX=192
    PARAM_CHAIN_MAX=192

    DEFAULTPARAM_N_EXPONENT=18
    DEFAULTPARAM_R=10
    DEFAULTPARAM_P=2
    DEFAULTPARAM_FORMAT="base64"
    DEFAULTPARAM_LENGTH=32
    
    ALTERNATE_PASTE_HOTKEY="E"
    ALTERNATE_PASTE_HOTKEY_SHIFT_MODIFIER=True
    ALTERNATE_PASTE_HOTKEY_CTRL_MODIFIER=True
    ALTERNATE_PASTE_HOTKEY_ALT_MODIFIER=False

    PURGE_VALUE=u"+"*max(PARAM_INPUT_MAX,PARAM_SALT_MAX,PARAM_LENGTH_MAX)
    PURGE_VALUE_RESULT=u"+"*(PARAM_LENGTH_MAX*8)
    
    RESULT_HIDING_CHARACTER="\u25cf"

    class UI_Signaller(QObject):
        active_signal=pyqtSignal(object)

        def __init__(self):
            super(ScryptCalc.UI_Signaller,self).__init__(None)
            return

        def SEND_EVENT(self,input_type,input_data={}):
            output_signal_info={"type":input_type,"data":input_data}
            try:
                self.active_signal.emit(output_signal_info)
                return True
            except:
                return False

    class Alternate_Paste_Agent(object):
        def __init__(self,input_UI_signaller):
            self.UI_signaller=input_UI_signaller
            self.request_exit=threading.Event()
            self.request_exit.clear()
            self.has_quit=threading.Event()
            self.has_quit.clear()
            self.result_updated=threading.Event()
            self.result_updated.clear()
            self.result_text_lock=threading.Lock()
            self.result_text=u""
            self.working_thread=threading.Thread(target=self.work_loop)
            self.working_thread.daemon=True
            return
        
        def START(self):
            keyboard.hook(self.on_key_press)
            self.working_thread.start()
            return

        def REQUEST_STOP(self):
            self.request_exit.set()
            return

        def IS_RUNNING(self):
            return self.has_quit.is_set()==False

        def CONCLUDE(self):
            global PENDING_ACTIVITY_HEARTBEAT_SECONDS

            while self.IS_RUNNING()==True:
                time.sleep(ScryptCalc.PENDING_ACTIVITY_HEARTBEAT_SECONDS)
            
            self.working_thread.join()
            del self.working_thread
            self.working_thread=None
            Cleanup_Memory()
            return
        
        def UPDATE_RESULT_TEXT(self,input_text):
            if self.request_exit.is_set()==False:
                self.result_text_lock.acquire()
                self.result_text=input_text
                self.result_updated.set()
                self.result_text_lock.release()
                
            input_text=ScryptCalc.PURGE_VALUE_RESULT
            del input_text
            input_text=""
            Cleanup_Memory()
            return
        
        def on_key_press(self,event):
            keyboard.unhook(self.on_key_press)
            
            if self.request_exit.is_set()==True:
                return
            
            if event.event_type!=keyboard.KEY_DOWN or event.name.upper()!=ScryptCalc.ALTERNATE_PASTE_HOTKEY:
                keyboard.hook(self.on_key_press)
                return
            
            if keyboard.is_pressed("shift")!=ScryptCalc.ALTERNATE_PASTE_HOTKEY_SHIFT_MODIFIER or keyboard.is_pressed("ctrl")!=ScryptCalc.ALTERNATE_PASTE_HOTKEY_CTRL_MODIFIER or keyboard.is_pressed("alt")!=ScryptCalc.ALTERNATE_PASTE_HOTKEY_ALT_MODIFIER:
                keyboard.hook(self.on_key_press)
                return
            
            self.UI_signaller.SEND_EVENT("result_requested",{})
            return
        
        def work_loop(self):
            result_length=-1
            current_character=None
            
            while self.request_exit.is_set()==False:
                time.sleep(ScryptCalc.PENDING_ACTIVITY_HEARTBEAT_SECONDS)
                
                if self.result_updated.is_set()==True:
                    self.result_text_lock.acquire()

                    result_length=len(self.result_text)
                    
                    if result_length>0:
                        keyboard.clear_all_hotkeys()

                    for result_character_index in range(result_length):
                        current_character=self.result_text[result_character_index]
                        keyboard.write(current_character,delay=0,exact=True)
                        
                        if self.request_exit.is_set()==True:
                            break
                        if result_character_index<result_length-1:
                            time.sleep(ScryptCalc.ALTERNATE_PASTE_INTERKEY_DELAY_SECONDS)
                    
                    if result_length>0:
                        keyboard.clear_all_hotkeys()
                    
                    result_length=-1
                    del current_character
                    current_character=None
                    self.result_text=ScryptCalc.PURGE_VALUE_RESULT
                    del self.result_text
                    self.result_text=u""
                    Cleanup_Memory()

                    self.result_updated.clear()
                    self.result_text_lock.release()

                    if self.request_exit.is_set()==False:
                        keyboard.hook(self.on_key_press)
                    
            keyboard.unhook_all()
            self.has_quit.set()
            return
        

    class Scrypt_Calculator(object):
        def __init__(self,input_UI_signaller):
            self.UI_signaller=input_UI_signaller
            self.request_exit=threading.Event()
            self.request_exit.clear()
            self.has_quit=threading.Event()
            self.has_quit.clear()
            self.abort_received=threading.Event()
            self.abort_received.clear()
            self.working_thread=threading.Thread(target=self.work_loop)
            self.working_thread.daemon=True
            self.lock_job=threading.Lock()
            self.job=None
            return

        def START(self):
            self.working_thread.start()
            return

        def REQUEST_STOP(self):
            self.request_exit.set()
            return

        def IS_RUNNING(self):
            return self.has_quit.is_set()==False

        def CONCLUDE(self):
            global PENDING_ACTIVITY_HEARTBEAT_SECONDS

            while self.IS_RUNNING()==True:
                time.sleep(ScryptCalc.PENDING_ACTIVITY_HEARTBEAT_SECONDS)
            
            self.working_thread.join()
            del self.working_thread
            self.working_thread=None
            Cleanup_Memory()
            return

        def REQUEST_COMPUTE(self,input_value,input_salt,input_R,input_N,input_P,input_length,input_chain):
            self.lock_job.acquire()
            self.abort_received.clear()
            self.job={"value":input_value,"salt":input_salt,"R":input_R,"N":input_N,"P":input_P,"length":input_length,"chain":input_chain}
            self.lock_job.release()

            input_value=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
            del input_value
            input_value=None
            input_salt=ScryptCalc.PURGE_VALUE
            del input_salt
            input_salt=None
            input_R=1
            input_N=1
            input_P=1
            input_length=1
            Cleanup_Memory()
            return

        def REQUEST_ABORT(self):
            self.abort_received.set()
            return

        def get_job(self):
            job_data=None
            self.lock_job.acquire()
            if self.job is not None:
                job_data=self.job
                self.job=ScryptCalc.PURGE_VALUE_RESULT
                del self.job
                self.job=None
            self.lock_job.release()
            Cleanup_Memory()
            return job_data
        
        def complete_job(self,input_result,input_compute_time_ms):
            self.UI_signaller.SEND_EVENT("compute_done",{"canceled":False,"result":input_result,"compute_time_ms":input_compute_time_ms})
            input_result=ScryptCalc.PURGE_VALUE
            del input_result
            input_result=None
            input_compute_time_ms=0
            del input_compute_time_ms
            input_compute_time_ms=None
            Cleanup_Memory()
            return
        
        def job_canceled(self):
            self.UI_signaller.SEND_EVENT("compute_done",{"canceled":True})
            return
        
        def update_chain_progress(self,input_passes_remaining):
            self.UI_signaller.SEND_EVENT("chain_progress",{"value":input_passes_remaining})
            return

        def work_loop(self):
            while self.request_exit.is_set()==False:
                time.sleep(ScryptCalc.PENDING_ACTIVITY_HEARTBEAT_SECONDS)
                new_job=self.get_job()
                if new_job is not None:
                    start_time=GetTickCount64()
                    value_bytes=bytes(new_job["value"],"utf-8")
                    new_job["value"]=ScryptCalc.PURGE_VALUE
                    del new_job["value"]
                    new_job["value"]=None
                    salt_bytes=bytes(new_job["salt"],"utf-8")
                    new_job["salt"]=ScryptCalc.PURGE_VALUE
                    del new_job["salt"]
                    new_job["salt"]=None
                    chain_pass=new_job["chain"]

                    while chain_pass>0:
                        chain_pass-=1
                        result=hashlib.scrypt(maxmem=ScryptCalc.COMPUTE_MEMORY_MAX_BYTES,password=value_bytes,salt=salt_bytes,n=new_job["N"],r=new_job["R"],p=new_job["P"],dklen=new_job["length"])
                        if self.abort_received.is_set()==True:
                            break
                        if chain_pass>0:
                            value_bytes=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
                            del value_bytes
                            value_bytes=None
                            value_bytes=result
                            self.update_chain_progress(chain_pass)

                    value_bytes=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
                    del value_bytes
                    value_bytes=None
                    salt_bytes=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
                    del salt_bytes
                    salt_bytes=None
                    new_job["N"]=1
                    new_job["R"]=1
                    new_job["P"]=1
                    new_job["length"]=1
                    new_job["chain"]=1
                    del new_job
                    new_job=None
                    new_job={}
                    
                    if self.abort_received.is_set()==False:
                        self.complete_job(result,GetTickCount64()-start_time)
                    
                    chain_pass=0
                    result=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
                    del result
                    result=None
                    
                    if self.abort_received.is_set()==True:
                        self.job_canceled()
                    
                    Cleanup_Memory()

            self.UI_signaller=None
            Cleanup_Memory()
            self.has_quit.set()
            return

    class UI(object):
        qtmsg_blacklist_startswith=["WARNING: QApplication was not created in the main()","OleSetClipboard: Failed to set mime data (text/plain) on clipboard: COM error"]

        class Text_Editor(QPlainTextEdit):
            def createMimeDataFromSelection(self):
                if self.parentWidget().copy_disabled==True:
                    return
                
                cursor=self.textCursor()
                start=cursor.selectionStart()
                end=cursor.selectionEnd()
                selected_text=self.parentWidget().stored_result_text[start:end]
                self.parentWidget().set_clipboard_text(selected_text)
                start=-1
                end=-1
                selected_text=ScryptCalc.PURGE_VALUE_RESULT
                del selected_text
                selected_text=None
                Cleanup_Memory()
                return None
            
        class Main_Window(QMainWindow):
            def __init__(self,input_parent_app,input_is_ready,input_is_exiting,input_has_quit,input_signaller,input_scrypt_calculator,input_alternate_paste_agent,input_settings):
                super(ScryptCalc.UI.Main_Window,self).__init__(None)

                self.parent_app=input_parent_app
                self.is_exiting=input_is_exiting
                self.has_quit=input_has_quit
                self.UI_signaller=input_signaller
                self.UI_signaller.active_signal.connect(self.signal_response_handler)
                self.scrypt_calculator=input_scrypt_calculator
                self.alternate_paste_agent=input_alternate_paste_agent
                self.param_N=-1
                self.memory_used_ok=False
                self.input_enabled=False
                self.waiting_for_result=False
                self.ignore_close=False

                self.UI_scale=self.logicalDpiX()/96.0
                self.signal_response_calls={"compute_done":self.compute_done,"chain_progress":self.update_chain_progress,"result_requested":self.on_alternate_paste}
                
                self.copy_disabled=False
                self.pending_clipboard_text=u""
                self.pending_post_clipboard_calls=[]
                
                self.timer_update_clipboard=QTimer(self)
                self.timer_update_clipboard.timeout.connect(self.set_clipboard_text_timer_event)
                self.timer_update_clipboard.setSingleShot(True)

                self.font_general=QFont("Arial")
                self.font_general.setPointSize(9)
                self.font_monospace=QFont("Consolas")
                self.font_monospace.setPointSize(10)

                self.setFixedSize(400*self.UI_scale,492*self.UI_scale)
                self.setWindowTitle("ScryptCalc")
                self.setWindowFlags(self.windowFlags()|Qt.MSWindowsFixedSizeDialogHint)
                
                icon_qba=QByteArray.fromBase64(ScryptCalc.APP_ICON_BASE64,QByteArray.Base64Encoding)
                icon_qimg=QImage.fromData(icon_qba,"PNG")
                del icon_qba
                icon_qpix=QPixmap.fromImage(icon_qimg)
                del icon_qimg
                app_icon=QIcon(icon_qpix)
                del icon_qpix
                self.setWindowIcon(app_icon)
                del app_icon
                del ScryptCalc.APP_ICON_BASE64
                ScryptCalc.APP_ICON_BASE64=None

                self.label_input=QLabel(self)
                self.label_input.setGeometry(10*self.UI_scale,0,120*self.UI_scale,26*self.UI_scale)
                self.label_input.setText("Input (password):")
                self.label_input.setFont(self.font_general)

                self.textbox_input=QLineEdit(self)
                self.textbox_input.setGeometry(10*self.UI_scale,20*self.UI_scale,380*self.UI_scale,26*self.UI_scale)
                self.textbox_input.setFont(self.font_monospace)
                self.textbox_input.setMaxLength(ScryptCalc.PARAM_INPUT_MAX)
                self.textbox_input.setAcceptDrops(False)
                self.textbox_input.setContextMenuPolicy(Qt.CustomContextMenu)

                self.checkbox_hide_input=QCheckBox(self)
                self.checkbox_hide_input.setGeometry(150*self.UI_scale,43*self.UI_scale,250*self.UI_scale,26*self.UI_scale)
                self.checkbox_hide_input.setText("Hide input")
                self.checkbox_hide_input.setFont(self.font_general)

                self.label_salt=QLabel(self)
                self.label_salt.setGeometry(10*self.UI_scale,56*self.UI_scale,100*self.UI_scale,26*self.UI_scale)
                self.label_salt.setText("Salt:")
                self.label_salt.setFont(self.font_general)

                self.textbox_salt=QLineEdit(self)
                self.textbox_salt.setGeometry(10*self.UI_scale,76*self.UI_scale,380*self.UI_scale,26*self.UI_scale)
                self.textbox_salt.setFont(self.font_monospace)
                self.textbox_salt.setMaxLength(ScryptCalc.PARAM_SALT_MAX)
                self.textbox_salt.setAcceptDrops(False)
                self.textbox_salt.setContextMenuPolicy(Qt.CustomContextMenu)

                self.checkbox_hide_salt=QCheckBox(self)
                self.checkbox_hide_salt.setGeometry(150*self.UI_scale,99*self.UI_scale,250*self.UI_scale,26*self.UI_scale)
                self.checkbox_hide_salt.setText("Hide salt")
                self.checkbox_hide_salt.setFont(self.font_general)

                self.label_N_exponent=QLabel(self)
                self.label_N_exponent.setGeometry(10*self.UI_scale,130*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_N_exponent.setText("Rounds (N) exponent:")
                self.label_N_exponent.setFont(self.font_general)

                self.label_N_total=QLabel(self)
                self.label_N_total.setGeometry(240*self.UI_scale,130*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_N_total.setFont(self.font_general)

                self.label_memory_usage=QLabel(self)
                self.label_memory_usage.setGeometry(240*self.UI_scale,155*self.UI_scale,200*self.UI_scale,26*self.UI_scale)
                self.label_memory_usage.setFont(self.font_general)

                self.spinbox_N_exponent=QSpinBox(self)
                self.spinbox_N_exponent.setGeometry(165*self.UI_scale,130*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_N_exponent.setRange(ScryptCalc.PARAM_N_EXPONENT_MIN,ScryptCalc.PARAM_N_EXPONENT_MAX)
                self.spinbox_N_exponent.setFont(self.font_general)
                self.spinbox_N_exponent.setValue(ScryptCalc.DEFAULTPARAM_N_EXPONENT)
                self.spinbox_N_exponent.setContextMenuPolicy(Qt.CustomContextMenu)

                self.label_R=QLabel(self)
                self.label_R.setGeometry(10*self.UI_scale,155*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_R.setText("Memory factor (R):")
                self.label_R.setFont(self.font_general)

                self.spinbox_R=QSpinBox(self)
                self.spinbox_R.setGeometry(165*self.UI_scale,155*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_R.setRange(ScryptCalc.PARAM_R_MIN,ScryptCalc.PARAM_R_MAX)
                self.spinbox_R.setFont(self.font_general)
                self.spinbox_R.setValue(ScryptCalc.DEFAULTPARAM_R)
                self.spinbox_R.setContextMenuPolicy(Qt.CustomContextMenu)

                self.label_P=QLabel(self)
                self.label_P.setGeometry(10*self.UI_scale,180*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_P.setFont(self.font_general)
                self.label_P.setText("Parallelism factor (P):")

                self.spinbox_P=QSpinBox(self)
                self.spinbox_P.setGeometry(165*self.UI_scale,180*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_P.setRange(ScryptCalc.PARAM_P_MIN,ScryptCalc.PARAM_P_MAX)
                self.spinbox_P.setFont(self.font_general)
                self.spinbox_P.setValue(ScryptCalc.DEFAULTPARAM_P)
                self.spinbox_P.setContextMenuPolicy(Qt.CustomContextMenu)

                self.label_length=QLabel(self)
                self.label_length.setGeometry(10*self.UI_scale,205*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_length.setText("Result length (bytes):")
                self.label_length.setFont(self.font_general)

                self.spinbox_length=QSpinBox(self)
                self.spinbox_length.setGeometry(165*self.UI_scale,205*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_length.setRange(1,ScryptCalc.PARAM_LENGTH_MAX)
                self.spinbox_length.setFont(self.font_general)
                self.spinbox_length.setValue(ScryptCalc.DEFAULTPARAM_LENGTH)
                self.spinbox_length.setContextMenuPolicy(Qt.CustomContextMenu)

                self.label_output_bits=QLabel(self)
                self.label_output_bits.setGeometry(240*self.UI_scale,205*self.UI_scale,80*self.UI_scale,26*self.UI_scale)
                self.label_output_bits.setFont(self.font_general)

                self.label_result_format=QLabel(self)
                self.label_result_format.setGeometry(10*self.UI_scale,230*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_result_format.setText("Result output format:")
                self.label_result_format.setFont(self.font_general)

                self.combobox_result_format=QComboBox(self)
                self.combobox_result_format.setGeometry(165*self.UI_scale,230*self.UI_scale,90*self.UI_scale,26*self.UI_scale)
                self.combobox_result_format.setFont(self.font_general)
                self.combobox_result_format.addItem("bin")
                self.combobox_result_format.addItem("hex")
                self.combobox_result_format.addItem("base32")
                self.combobox_result_format.addItem("base64")
                self.combobox_result_format.addItem("base85")
                format_index=self.combobox_result_format.findText(ScryptCalc.DEFAULTPARAM_FORMAT)
                self.combobox_result_format.setCurrentIndex(format_index)

                self.checkbox_clear_input_asap=QCheckBox(self)
                self.checkbox_clear_input_asap.setGeometry(75*self.UI_scale,255*self.UI_scale,250*self.UI_scale,26*self.UI_scale)
                self.checkbox_clear_input_asap.setText("Clear password input field on compute")
                self.checkbox_clear_input_asap.setFont(self.font_general)

                self.label_chain=QLabel(self)
                self.label_chain.setGeometry(10*self.UI_scale,282*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_chain.setText("Chain multiple passes:")
                self.label_chain.setFont(self.font_general)

                self.spinbox_chain=QSpinBox(self)
                self.spinbox_chain.setGeometry(165*self.UI_scale,282*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_chain.setRange(1,ScryptCalc.PARAM_CHAIN_MAX)
                self.spinbox_chain.setFont(self.font_general)
                self.spinbox_chain.setValue(1)
                self.spinbox_chain.setContextMenuPolicy(Qt.CustomContextMenu)

                self.button_compute_abort=QPushButton(self)
                self.button_compute_abort.setGeometry(250*self.UI_scale,282*self.UI_scale,90*self.UI_scale,26*self.UI_scale)
                self.button_compute_abort.setText("Compute")
                self.button_compute_abort.setFont(self.font_general)

                self.label_result_info=QLabel(self)
                self.label_result_info.setGeometry(20*self.UI_scale,307*self.UI_scale,300*self.UI_scale,26*self.UI_scale)
                self.label_result_info.setText("Result (derived key):")
                self.label_result_info.setFont(self.font_general)

                self.button_copy=QPushButton(self)
                self.button_copy.setGeometry(336*self.UI_scale,345*self.UI_scale,60*self.UI_scale,52*self.UI_scale)
                self.button_copy.setText("Copy\nresult")
                self.button_copy.setFont(self.font_general)

                self.result_bytes=bytes()
                self.stored_result_text=u""
                
                self.textedit_result=ScryptCalc.UI.Text_Editor(self)
                self.textedit_result.setReadOnly(True)
                self.textedit_result.setGeometry(5*self.UI_scale,329*self.UI_scale,328*self.UI_scale,82*self.UI_scale)
                self.textedit_result.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                self.textedit_result.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.textedit_result.verticalScrollBar().setStyleSheet(f"QScrollBar:vertical {chr(123)}border:{str(round(1*self.UI_scale))}px; width:{str(round(15*self.UI_scale))}px solid;{chr(125)}")
                self.textedit_result.setFont(self.font_monospace)
                self.textedit_result.setWordWrapMode(QTextOption.WrapAnywhere)
                self.textedit_result.setUndoRedoEnabled(False)
                document=self.textedit_result.document()
                document.setUndoRedoEnabled(False)
                document.setUseDesignMetrics(False)
                document.setMaximumBlockCount(0)
                self.textedit_result.setAcceptDrops(False)
                self.textedit_result.setContextMenuPolicy(Qt.CustomContextMenu)
                self.textedit_result.customContextMenuRequested.connect(self.result_context_menu_show)

                self.checkbox_hide_result=QCheckBox(self)
                self.checkbox_hide_result.setGeometry(150*self.UI_scale,409*self.UI_scale,250*self.UI_scale,26*self.UI_scale)
                self.checkbox_hide_result.setText("Hide result")
                self.checkbox_hide_result.setFont(self.font_general)

                self.label_result_fingerprint=QLabel(self)
                self.label_result_fingerprint.setGeometry(90*self.UI_scale,432*self.UI_scale,125*self.UI_scale,26*self.UI_scale)
                self.label_result_fingerprint.setText("Fingerprint:")
                self.label_result_fingerprint.setFont(self.font_monospace)

                self.checkbox_clear_clipboard_on_exit=QCheckBox(self)
                self.checkbox_clear_clipboard_on_exit.setGeometry(115*self.UI_scale,462*self.UI_scale,250*self.UI_scale,26*self.UI_scale)
                self.checkbox_clear_clipboard_on_exit.setText("Clear clipboard on exit")
                self.checkbox_clear_clipboard_on_exit.setFont(self.font_general)

                self.context_menu=QMenu(self)

                self.clipboard=QApplication.clipboard()
                
                self.checkbox_hide_input.toggled.connect(lambda new_state:self.set_textbox_input_hidden(self.textbox_input,new_state))
                self.checkbox_hide_salt.toggled.connect(lambda new_state:self.set_textbox_input_hidden(self.textbox_salt,new_state))
                self.checkbox_hide_result.toggled.connect(lambda new_state:self.set_textbox_input_hidden(self.textedit_result,new_state))

                if input_settings is not None:
                    if input_settings["title"] is not None:
                        self.setWindowTitle(f"ScryptCalc: {input_settings['title']}")
                        input_settings["title"]=ScryptCalc.PURGE_VALUE
                        del input_settings["title"]
                        input_settings["title"]=None
                    if input_settings["hideinput"] is not None:
                        self.checkbox_hide_input.setChecked(input_settings["hideinput"])
                        input_settings["hideinput"]=False
                        del input_settings["hideinput"]
                        input_settings["hideinput"]=None
                    if input_settings["hidesalt"] is not None:
                        self.checkbox_hide_salt.setChecked(input_settings["hidesalt"])
                        input_settings["hidesalt"]=False
                        del input_settings["hidesalt"]
                        input_settings["hidesalt"]=None
                    if input_settings["hideresult"] is not None:
                        self.checkbox_hide_result.setChecked(input_settings["hideresult"])
                        input_settings["hideresult"]=False
                        del input_settings["hideresult"]
                        input_settings["hideresult"]=None
                    if input_settings["format"] is not None:
                        format_index=self.combobox_result_format.findText(input_settings["format"])
                        self.combobox_result_format.setCurrentIndex(format_index)
                        input_settings["format"]=ScryptCalc.PURGE_VALUE
                        del input_settings["format"]
                        input_settings["format"]=None
                    if input_settings["salt"] is not None:
                        self.textbox_salt.setText(input_settings["salt"])
                        input_settings["salt"]=ScryptCalc.PURGE_VALUE
                        del input_settings["salt"]
                        input_settings["salt"]=None
                    if input_settings["N_exp"] is not None:
                        self.spinbox_N_exponent.setValue(input_settings["N_exp"])
                        input_settings["N_exp"]=1
                        del input_settings["N_exp"]
                        input_settings["N_exp"]=None
                    if input_settings["P"] is not None:
                        self.spinbox_P.setValue(input_settings["P"])
                        input_settings["P"]=1
                        del input_settings["P"]
                        input_settings["P"]=None
                    if input_settings["R"] is not None:
                        self.spinbox_R.setValue(input_settings["R"])
                        input_settings["R"]=1
                        del input_settings["R"]
                        input_settings["R"]=None
                    if input_settings["length"] is not None:
                        self.spinbox_length.setValue(input_settings["length"])
                        input_settings["length"]=1
                        del input_settings["length"]
                        input_settings["length"]=None
                    if input_settings["chain"] is not None:
                        self.spinbox_chain.setValue(input_settings["chain"])
                        input_settings["chain"]=1
                        del input_settings["chain"]
                        input_settings["chain"]=None
                    if input_settings["clearinput"] is not None:
                        self.checkbox_clear_input_asap.setChecked(input_settings["clearinput"])
                        input_settings["clearinput"]=False
                        del input_settings["clearinput"]
                        input_settings["clearinput"]=None
                    if input_settings["clearclipboard"] is not None:
                        self.checkbox_clear_clipboard_on_exit.setChecked(input_settings["clearclipboard"])
                        input_settings["clearclipboard"]=False
                        del input_settings["clearclipboard"]
                        input_settings["clearclipboard"]=None
                    if input_settings["nocopy"] is not None:
                        self.copy_disabled=input_settings["nocopy"]
                        input_settings["nocopy"]=False
                        del input_settings["nocopy"]
                        input_settings["nocopy"]=None
                        
                    del input_settings
                    input_settings={}
                
                self.textbox_input.textChanged.connect(self.textbox_input_onchange)
                self.textbox_input.returnPressed.connect(self.compute_abort_go)
                self.textbox_input.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.textbox_input))
                self.textbox_salt.textChanged.connect(self.textbox_salt_onchange)
                self.textbox_salt.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.textbox_salt))
                self.spinbox_N_exponent.valueChanged.connect(self.spinbox_N_exponent_onchange)
                self.spinbox_N_exponent.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.spinbox_N_exponent))
                self.spinbox_P.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.spinbox_P))
                self.spinbox_R.valueChanged.connect(self.spinbox_R_onchange)
                self.spinbox_R.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.spinbox_R))
                self.spinbox_length.valueChanged.connect(self.update_output_bits_label)
                self.spinbox_length.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.spinbox_length))
                self.spinbox_chain.customContextMenuRequested.connect(lambda:self.lineedit_context_menu_show(self.spinbox_length))
                self.combobox_result_format.currentIndexChanged.connect(self.combobox_result_format_onindexchanged)
                self.button_compute_abort.clicked.connect(self.compute_abort_go)
                self.button_copy.clicked.connect(self.button_copy_onclick)

                self.update_N_param()
                self.update_memory_usage()
                self.update_output_bits_label()
                self.set_input_enabled(True)
                
                Cleanup_Memory()
                input_is_ready.set()
                return
            
            def set_clipboard_text(self,input_text,post_clipboard_calls=[]):
                if self.copy_disabled==False:
                    self.pending_clipboard_text=input_text
                    
                self.pending_post_clipboard_calls=post_clipboard_calls+self.pending_post_clipboard_calls
                self.timer_update_clipboard.start(0)
                input_text=ScryptCalc.PURGE_VALUE_RESULT
                del input_text
                input_text=u""
                Cleanup_Memory()
                return
            
            def set_clipboard_text_timer_event(self):
                if self.is_exiting.is_set()==True:
                    return
                
                start_time=GetTickCount64()
                while self.clipboard.text()!=self.pending_clipboard_text and (GetTickCount64()-start_time)<ScryptCalc.CLIPBOARD_SET_TIMEOUT_MILLISECONDS:
                    self.clipboard.setText(self.pending_clipboard_text)
                    QCoreApplication.processEvents()
                self.pending_clipboard_text=ScryptCalc.PURGE_VALUE_RESULT
                del self.pending_clipboard_text
                self.pending_clipboard_text=u""
                Cleanup_Memory()
                
                if len(self.pending_post_clipboard_calls)>0:
                    pending_call=self.pending_post_clipboard_calls[0]
                    self.pending_post_clipboard_calls.pop(0)
                    pending_call()
                return
            
            def clear_result_field(self):
                cursor=self.textedit_result.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.textedit_result.setTextCursor(cursor)
                cursor.movePosition(QTextCursor.Start)
                self.textedit_result.setTextCursor(cursor)
                cursor=None
                self.textedit_result.document().clearUndoRedoStacks()
                self.textedit_result.document().setPlainText(ScryptCalc.PURGE_VALUE_RESULT)
                self.textedit_result.document().setPlainText(u"")
                self.textedit_result.document().clear()
                Cleanup_Memory()
                return
            
            def textbox_input_onchange(self):
                initial_cursor_pos=self.textbox_input.cursorPosition()
                initial_text=self.textbox_input.text()
                initial_text_len=len(initial_text)
                final_text=initial_text.replace(" ","").replace("\r","").replace("\n","")
                final_text_len=len(final_text)
                self.textbox_input.setText(final_text)
                new_cursor_pos=max(min(initial_cursor_pos-(initial_text_len-final_text_len),final_text_len),0)
                self.textbox_input.setCursorPosition(new_cursor_pos)
                initial_cursor_pos=-1
                new_cursor_pos=-1
                initial_text_len=-1
                initial_text=ScryptCalc.PURGE_VALUE
                del initial_text
                initial_text=None
                final_text_len=-1
                final_text=ScryptCalc.PURGE_VALUE
                del final_text
                final_text=None
                Cleanup_Memory()
                return

            def textbox_salt_onchange(self):
                initial_cursor_pos=self.textbox_salt.cursorPosition()
                initial_text=self.textbox_salt.text()
                initial_text_len=len(initial_text)
                final_text=initial_text.replace(" ","").replace("\r","").replace("\n","")
                final_text_len=len(final_text)
                self.textbox_salt.setText(final_text)
                new_cursor_pos=max(min(initial_cursor_pos-(initial_text_len-final_text_len),final_text_len),0)
                self.textbox_salt.setCursorPosition(new_cursor_pos)
                initial_text_len=-1
                initial_text=ScryptCalc.PURGE_VALUE
                del initial_text
                initial_text=None
                final_text_len=-1
                final_text=ScryptCalc.PURGE_VALUE
                del final_text
                final_text=None
                Cleanup_Memory()
                return

            def on_alternate_paste(self,_):
                self.alternate_paste_agent.UPDATE_RESULT_TEXT(self.stored_result_text)
                return

            def combobox_result_format_onindexchanged(self):
                self.display_result()
                return

            def set_input_enabled(self,input_state):
                if input_state!=self.input_enabled:
                    self.input_enabled=input_state
                    self.textedit_result.setEnabled(input_state)
                    self.textbox_input.setEnabled(input_state)
                    self.checkbox_hide_input.setEnabled(input_state)
                    self.textbox_salt.setEnabled(input_state)
                    self.checkbox_hide_salt.setEnabled(input_state)
                    self.spinbox_length.setEnabled(input_state)
                    self.spinbox_N_exponent.setEnabled(input_state)
                    self.spinbox_R.setEnabled(input_state)
                    self.spinbox_P.setEnabled(input_state)
                    self.combobox_result_format.setEnabled(input_state)
                    self.checkbox_hide_result.setEnabled(input_state)
                    self.checkbox_clear_input_asap.setEnabled(input_state)
                    self.checkbox_clear_clipboard_on_exit.setEnabled(input_state)
                    self.spinbox_chain.setEnabled(input_state)
                    self.update_button_state()
                return

            def update_button_state(self):
                self.button_compute_abort.setEnabled(self.input_enabled and self.memory_used_ok)
                result_text=self.textedit_result.document().toRawText()
                result_not_empty=len(result_text)>0
                result_text=ScryptCalc.PURGE_VALUE_RESULT
                del result_text
                result_text=None
                Cleanup_Memory()
                self.button_copy.setEnabled(self.input_enabled and result_not_empty and self.copy_disabled==False)
                result_not_empty=False
                return
            
            def set_textbox_input_hidden(self,target_object,hidden_state):
                if type(target_object) is ScryptCalc.UI.Text_Editor:
                    if hidden_state==True:
                        target_object.document().setPlainText(ScryptCalc.RESULT_HIDING_CHARACTER*len(self.stored_result_text))
                    else:
                        self.display_result()
                    return
                
                if hidden_state==True:
                    new_state=QLineEdit.EchoMode.Password
                else:
                    new_state=QLineEdit.EchoMode.Normal 
                target_object.setEchoMode(new_state)
                return

            @staticmethod
            def readable_size(input_size):
                if input_size<1024:
                    return f"{str(input_size)} Bytes"
                if input_size<1024**2:
                    return f"{str(round(input_size/1024.0,2))} KB"
                if input_size<1024**3:
                    return f"{str(round(input_size/1024.0**2,2))} MB"
                return f"{str(round(input_size/1024.0**3,2))} GB"

            def update_memory_usage(self):
                memory_used=self.param_N*self.spinbox_R.value()*128
                if memory_used>ScryptCalc.COMPUTE_MEMORY_MAX_BYTES:
                    self.label_memory_usage.setText(f"Est. memory > {ScryptCalc.UI.Main_Window.readable_size(ScryptCalc.COMPUTE_MEMORY_MAX_BYTES)} limit!")
                    self.label_memory_usage.setStyleSheet("font-weight: bold")
                    self.memory_used_ok=False
                else:
                    self.label_memory_usage.setText(f"Est. memory: {ScryptCalc.UI.Main_Window.readable_size(memory_used)}")
                    self.label_memory_usage.setStyleSheet("")
                    self.memory_used_ok=True
                self.update_button_state()
                return
            
            def update_output_bits_label(self):
                self.label_output_bits.setText(f"{self.spinbox_length.value()*8} bits")
                return

            def update_N_param(self):
                n_exp=self.spinbox_N_exponent.value()
                self.param_N=2**n_exp
                self.label_N_total.setText(f"Total rounds: {self.param_N}")
                if n_exp>=16:
                    self.spinbox_R.setRange(2,ScryptCalc.PARAM_R_MAX)
                elif ScryptCalc.PARAM_R_MIN<2:
                    self.spinbox_R.setRange(ScryptCalc.PARAM_R_MIN,ScryptCalc.PARAM_R_MAX)
                return

            def spinbox_R_onchange(self):
                self.update_memory_usage()
                return

            def spinbox_N_exponent_onchange(self):
                self.update_N_param()
                self.update_memory_usage()
                return

            def compute_abort_go(self):
                if self.button_compute_abort.isEnabled()==False:
                    return

                if self.button_compute_abort.text()=="Abort":
                    self.button_compute_abort.setEnabled(False)
                    self.label_result_info.setText("Aborting compute...")
                    self.scrypt_calculator.REQUEST_ABORT()
                    return
                
                self.set_input_enabled(False)
                self.clear_result_field()
                self.purge_result_bytes()
                self.purge_result_info()
                self.waiting_for_result=True
                if self.spinbox_chain.value()==1:
                    self.label_result_info.setText("Computing...")
                else:
                    self.label_result_info.setText(f"Computing: {self.spinbox_chain.value()} passes remaining...")
                    self.button_compute_abort.setEnabled(True)
                    self.button_compute_abort.setText("Abort")
                
                self.scrypt_calculator.REQUEST_COMPUTE(self.textbox_input.text(),self.textbox_salt.text(),self.spinbox_R.value(),self.param_N,self.spinbox_P.value(),self.spinbox_length.value(),self.spinbox_chain.value())

                if self.checkbox_clear_input_asap.isChecked()==True:
                    ScryptCalc.UI.Main_Window.purge_lineedit_data(self.textbox_input)
                return
            
            def button_copy_onclick(self):
                self.set_clipboard_text(self.stored_result_text)
                Cleanup_Memory()
                return

            def signal_response_handler(self,event):
                if self.is_exiting.is_set()==True:
                    event["data"]=ScryptCalc.PURGE_VALUE_RESULT
                    del event["data"]
                    event["data"]=None
                    return

                event_type=event["type"]
                if event_type in self.signal_response_calls:
                    self.signal_response_calls[event_type](event["data"])
                    event["data"]=ScryptCalc.PURGE_VALUE_RESULT
                    del event["data"]
                    event["data"]=None

                return

            def reenable_close_and_call(self):
                self.ignore_close=False
                self.close()
                return

            def closeEvent(self,event):
                if self.ignore_close==True or self.is_exiting.is_set()==True or self.waiting_for_result==True:
                    event.ignore()
                    return
                
                self.set_input_enabled(False)
                
                if self.checkbox_clear_clipboard_on_exit.checkState()==Qt.Checked:
                    self.checkbox_clear_clipboard_on_exit.setChecked(False)
                    self.ignore_close=True
                    self.set_clipboard_text(ScryptCalc.PURGE_VALUE_RESULT,[lambda:self.set_clipboard_text(ScryptCalc.PURGE_VALUE_RESULT),lambda:self.set_clipboard_text(u""),self.reenable_close_and_call])
                    event.ignore()
                    return

                self.is_exiting.set()
                
                self.copy_disabled=False
                self.purge_result_bytes()
                ScryptCalc.UI.Main_Window.purge_lineedit_data(self.textbox_input)
                ScryptCalc.UI.Main_Window.purge_lineedit_data(self.textbox_salt)
                self.purge_result_info()
                self.setWindowTitle(ScryptCalc.PURGE_VALUE)
                self.setWindowTitle("ScryptCalc")
                self.spinbox_N_exponent.setValue(1)
                self.spinbox_R.setValue(1)
                self.spinbox_P.setValue(1)
                self.spinbox_length.setValue(1)
                self.spinbox_chain.setValue(1)
                self.textbox_input.destroy()
                del self.textbox_input
                self.textbox_input=None
                self.textbox_salt.destroy()
                del self.textbox_salt
                self.textbox_salt=None
                self.combobox_result_format.setCurrentIndex(1)
                self.clear_result_field()
                self.textedit_result.destroy()
                del self.textedit_result
                self.textedit_result=None
                QCoreApplication.processEvents()
                self.UI_signaller=None
                self.parent_app=None
                Cleanup_Memory()
                self.has_quit.set()
                return

            def compute_done(self,result_data):
                if result_data["canceled"]==False:
                    self.result_bytes=result_data["result"]
                    self.label_result_info.setText(f"Result (derived key) took {round(result_data['compute_time_ms']/1000.0,3)} second(s):")
                    result_data["result"]=ScryptCalc.PURGE_VALUE
                    del result_data["result"]
                    result_data["result"]=None
                    result_data["compute_time_ms"]=ScryptCalc.PURGE_VALUE
                    del result_data["compute_time_ms"]
                    result_data["compute_time_ms"]=None
                else:
                    self.label_result_info.setText(ScryptCalc.PURGE_VALUE)
                    self.purge_result_info()

                result_data["result"]=bytes(ScryptCalc.PURGE_VALUE_RESULT,"utf-8")
                del result_data
                result_data=None
                result_data={}
                Cleanup_Memory()
                self.button_compute_abort.setText("Compute")
                self.set_input_enabled(True)
                self.waiting_for_result=False
                self.display_result()
                self.button_copy.setFocus()
                self.parent_app.alert(self)
                return
            
            def update_chain_progress(self,update_data):
                passes_remaining=update_data["value"]
                if passes_remaining>1:
                    self.label_result_info.setText(f"Computing: {passes_remaining} passes remaining...")
                else:
                    self.label_result_info.setText("Computing: 1 pass remaining...")
                    self.button_compute_abort.setEnabled(False)
                passes_remaining=0
                del update_data["value"]
                update_data["value"]=None
                return

            def display_result(self):
                self.stored_result_text=ScryptCalc.PURGE_VALUE_RESULT
                self.stored_result_text=u""
                Cleanup_Memory()

                result_format=self.combobox_result_format.itemText(self.combobox_result_format.currentIndex())
                text_value=""

                if result_format=="bin" and len(self.result_bytes)>0:
                    text_value="{:08b}".format(int(self.result_bytes.hex(),16))
                elif result_format=="hex":
                    text_value=self.result_bytes.hex()
                elif result_format=="base32":
                    text_value=base64.b32encode(self.result_bytes).decode("utf-8")
                elif result_format=="base64":
                    text_value=base64.b64encode(self.result_bytes).decode("utf-8")
                elif result_format=="base85":
                    text_value=base64.b85encode(self.result_bytes).decode("utf-8")

                self.stored_result_text=text_value
                text_value=ScryptCalc.PURGE_VALUE_RESULT
                del text_value
                text_value=None
                if self.checkbox_hide_result.checkState()==Qt.Checked:
                    self.textedit_result.document().setPlainText(ScryptCalc.RESULT_HIDING_CHARACTER*len(self.stored_result_text))
                else:
                    self.textedit_result.document().setPlainText(self.stored_result_text)
                    
                if len(self.stored_result_text)>0:
                    self.label_result_fingerprint.setText(f"Fingerprint: {ScryptCalc.PURGE_VALUE}")
                    self.label_result_fingerprint.setText("Fingerprint:")
                    result_hash=hashlib.sha3_512()
                    result_hash.update(bytes(self.stored_result_text,"utf-8"))
                    fingerprint_data=base64.b32encode(result_hash.digest()).decode("utf-8")[18:21]
                    self.label_result_fingerprint.setText(f"Fingerprint: {fingerprint_data}")
                    del fingerprint_data
                    fingerprint_data=None
                    del result_hash
                    result_hash=None
                    
                Cleanup_Memory()
                self.update_button_state()
                return

            def purge_result_info(self):
                self.label_result_info.setText(ScryptCalc.PURGE_VALUE_RESULT)
                self.label_result_info.setText("Result (derived key):")
                self.stored_result_text=ScryptCalc.PURGE_VALUE_RESULT
                self.stored_result_text=u""
                self.label_result_fingerprint.setText(ScryptCalc.PURGE_VALUE_RESULT)
                self.label_result_fingerprint.setText("Fingerprint:")
                Cleanup_Memory()
                return

            def purge_result_bytes(self):
                self.result_bytes=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
                del self.result_bytes
                self.result_bytes=bytes()
                Cleanup_Memory()
                return

            @staticmethod
            def purge_lineedit_data(input_item):
                input_item.deselect()
                input_item.setSelection(0,0)
                input_item.setCursorPosition(0)
                max_length=input_item.maxLength()
                input_item.setMaxLength(0)
                input_item.clear()
                input_item.setMaxLength(max_length)
                max_length=-1
                input_item.setText(ScryptCalc.PURGE_VALUE)
                input_item.setSelection(0,0)
                input_item.setCursorPosition(0)
                input_item.setText(u"")
                Cleanup_Memory()
                return

            def lineedit_context_menu_show(self,source_item):
                self.context_menu.clear()
                validating_item=None
                if type(source_item)!=QLineEdit:
                    validating_item=source_item
                    source_item=source_item.findChild(QLineEdit)
                    if source_item is None:
                        return
                
                item_text_length=len(source_item.text())
                if item_text_length>0:
                    menu_action=self.context_menu.addAction("Select &All")
                    menu_action.setFont(self.font_general)
                    menu_action.setShortcut(QKeySequence(Qt.Key_A))
                    menu_action.triggered.connect(lambda:source_item.selectAll())
                    if source_item.hasSelectedText()==True:
                        
                        if self.copy_disabled==False:
                            self.context_menu.addSeparator()
                            menu_action=self.context_menu.addAction("&Copy Selection")
                            menu_action.setFont(self.font_general)
                            menu_action.setShortcut(QKeySequence(Qt.Key_C))
                            menu_action.triggered.connect(lambda:self.set_clipboard_text(source_item.selectedText()))
                            menu_action=self.context_menu.addAction("Cu&t Selection")
                            menu_action.setFont(self.font_general)
                            menu_action.setShortcut(QKeySequence(Qt.Key_T))
                            menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.lineedit_context_menu_cut_selection(self,source_item))
                            
                        menu_action=self.context_menu.addAction("&Delete Selection")
                        menu_action.setFont(self.font_general)
                        menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.lineedit_context_menu_delete_selection(source_item))
                        menu_action.setShortcut(QKeySequence(Qt.Key_D))
                        self.context_menu.addSeparator()
                        menu_action=self.context_menu.addAction("D&eselect")
                        menu_action.setFont(self.font_general)
                        menu_action.triggered.connect(lambda:source_item.deselect())
                        menu_action.setShortcut(QKeySequence(Qt.Key_E))
                if len(self.clipboard.text())>0:
                    if source_item.hasSelectedText()==True:
                        menu_action=self.context_menu.addAction("&Paste Over Selection")
                        menu_action.setFont(self.font_general)
                        menu_action.triggered.connect(lambda:[ScryptCalc.UI.Main_Window.lineedit_context_menu_paste_over_selection(source_item,self.clipboard),ScryptCalc.UI.Main_Window.validate_value(validating_item)])
                    else:
                        menu_action=self.context_menu.addAction("&Paste")
                        menu_action.setFont(self.font_general)
                        menu_action.triggered.connect(lambda:[ScryptCalc.UI.Main_Window.lineedit_context_menu_paste(source_item,self.clipboard),ScryptCalc.UI.Main_Window.validate_value(validating_item)])
                        menu_action.setShortcut(QKeySequence(Qt.Key_P))
                
                if item_text_length>0:
                    self.context_menu.addSeparator()
                    menu_action=self.context_menu.addAction("Clea&r")
                    menu_action.setFont(self.font_general)
                    menu_action.setShortcut(QKeySequence(Qt.Key_R))
                    menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.purge_lineedit_data(source_item))
                
                item_text_length=-1
                if len(self.context_menu.actions())>0:
                    self.context_menu.exec_(QCursor.pos())
                    self.context_menu.close()
                    self.context_menu.clear()
                    
                Cleanup_Memory()
                source_item.setFocus()
                return
        
            def result_context_menu_show(self):
                self.context_menu.clear()

                cursor=self.textedit_result.textCursor()
                cursor_start=cursor.selectionStart()
                cursor_end=cursor.selectionEnd()
                item_text_length=len(self.stored_result_text)
                if item_text_length>0:
                    menu_action=self.context_menu.addAction("Select &All")
                    menu_action.setFont(self.font_general)
                    menu_action.setShortcut(QKeySequence(Qt.Key_A))
                    menu_action.triggered.connect(lambda:self.textedit_result.selectAll())
                    
                    if cursor_start!=-1 and cursor_end!=-1 and cursor_start<cursor_end:
                        if self.copy_disabled==False:
                            self.context_menu.addSeparator()
                            menu_action=self.context_menu.addAction("&Copy Selection")
                            menu_action.setFont(self.font_general)
                            menu_action.setShortcut(QKeySequence(Qt.Key_C))
                            menu_action.triggered.connect(lambda:self.set_clipboard_text(self.stored_result_text[cursor_start:cursor_end]))
                            
                        self.context_menu.addSeparator()
                        menu_action=self.context_menu.addAction("D&eselect")
                        menu_action.setFont(self.font_general)
                        menu_action.triggered.connect(lambda:[cursor.movePosition(QTextCursor.End),self.textedit_result.setTextCursor(cursor)])
                        menu_action.setShortcut(QKeySequence(Qt.Key_E))
                        
                item_text_length=-1
                if len(self.context_menu.actions())>0:
                    self.context_menu.exec_(QCursor.pos())
                    self.context_menu.close()
                    self.context_menu.clear()
                    
                cursor=None
                cursor_start=-1
                cursor_end=-1
                Cleanup_Memory()
                self.textedit_result.setFocus()
                return

            @staticmethod
            def lineedit_context_menu_cut_selection(parent,source_item):
                parent.set_clipboard_text(source_item.selectedText())
                old_position=source_item.cursorPosition()
                source_item.setText(f"{source_item.text()[:source_item.selectionStart()]}{source_item.text()[source_item.selectionEnd():]}")
                source_item.setCursorPosition(old_position)
                return
    
            @staticmethod
            def lineedit_context_menu_delete_selection(source_item):
                old_selection_start=source_item.selectionStart()
                source_item.setText(f"{source_item.text()[:source_item.selectionStart()]}{source_item.text()[source_item.selectionEnd():]}")
                source_item.setCursorPosition(old_selection_start)
                return
    
            @staticmethod
            def lineedit_context_menu_paste_over_selection(source_item,clipboard):
                old_selection_start=source_item.selectionStart()
                source_item.setText(f"{source_item.text()[:source_item.selectionStart()]}{clipboard.text()}{source_item.text()[source_item.selectionEnd():]}")
                source_item.setCursorPosition(old_selection_start+len(clipboard.text()))
                return
    
            @staticmethod
            def lineedit_context_menu_paste(source_item,clipboard):
                old_position=source_item.cursorPosition()
                source_item.setText(f"{source_item.text()[:source_item.cursorPosition()]}{clipboard.text()}{source_item.text()[source_item.cursorPosition():]}")
                source_item.setCursorPosition(old_position+len(clipboard.text()))
                return

            @staticmethod
            def validate_value(validating_item):
                if validating_item is not None:
                    validating_item.clearFocus()
                    validating_item.setFocus()
                return

        def __init__(self,input_signaller,input_scrypt_calculator,input_alternate_paste_agent,input_settings=None):
            qInstallMessageHandler(self.qtmsg_handler)
            self.is_ready=threading.Event()
            self.is_ready.clear()
            self.is_exiting=threading.Event()
            self.is_exiting.clear()
            self.has_quit=threading.Event()
            self.has_quit.clear()
            self.UI_signaller=input_signaller
            self.scrypt_calculator=input_scrypt_calculator
            self.alternate_paste_agent=input_alternate_paste_agent
            self.startup_settings=input_settings
            self.working_thread=threading.Thread(target=self.run_UI)
            self.working_thread.daemon=True
            self.working_thread.start()
            input_settings=ScryptCalc.PURGE_VALUE_RESULT
            del input_settings
            input_settings=None
            return

        def __del__(self):
            qInstallMessageHandler(None)
            return

        @staticmethod
        def qtmsg_handler(msg_type,msg_log_context,msg_string):
            for entry in ScryptCalc.UI.qtmsg_blacklist_startswith:
                if msg_string.startswith(entry):
                    return

            sys.stderr.write(f"{msg_string}\n")
            return

        def run_UI(self):
            self.UI_app=QApplication([])
            self.UI_app.setAttribute(Qt.AA_DisableWindowContextHelpButton,True)
            self.UI_app.setStyle("fusion")
            self.UI_window=ScryptCalc.UI.Main_Window(self.UI_app,self.is_ready,self.is_exiting,self.has_quit,self.UI_signaller,self.scrypt_calculator,self.alternate_paste_agent,self.startup_settings)
            self.UI_window.show()
            self.UI_app.aboutToQuit.connect(self.UI_app.deleteLater)
            self.UI_window.raise_()
            self.UI_window.activateWindow()
            self.startup_settings=ScryptCalc.PURGE_VALUE_RESULT
            del self.startup_settings
            self.startup_settings=None
            
            sys.exit(self.UI_app.exec_())
            
            self.UI_window.destroy()
            del self.UI_window
            self.UI_window=None
            self.UI_app.close
            del self.UI_app
            self.UI_app=None
            Cleanup_Memory()
            return

        def IS_RUNNING(self):
            return self.has_quit.is_set()==False

        def IS_READY(self):
            return self.is_ready.is_set()==True
        
        def CONCLUDE(self):
            self.working_thread.join()
            del self.working_thread
            self.working_thread=None
            Cleanup_Memory()
            return

    @staticmethod
    def sanitize_settings_string(input_string):
        collected_settings={}

        if len(input_string)>0:
            try:
                settings_lines=[line.strip() for line in input_string.split("\n") if line.strip()]
            except:
                settings_lines=[input_string]

            for line in settings_lines:
                separator_pos=line.find("=")
                if separator_pos>-1:
                    key=line[:separator_pos].lower().strip()
                    value=line[separator_pos+1:].strip()
                    if key in ["title","format","salt","nexp","p","r","length","clearinput","hideinput","hidesalt","chain","hideresult","clearclipboard","nocopy"]:
                        if key=="nexp":
                            key="N_exp"
                        if key in ["p", "r"]:
                            key=key.upper()

                        valid_value=True
                        
                        if len(value)>0 and len(value)<=ScryptCalc.PARAM_LENGTH_MAX:
                            if key in ["N_exp","P","R","length","chain"]:
                                if len(value)>3:
                                    valid_value=False
                                else:
                                    try:
                                        value=int(value)
                                    except:
                                        valid_value=False

                                if valid_value==True:
                                    if key=="N_exp" and (value<ScryptCalc.PARAM_N_EXPONENT_MIN or value>ScryptCalc.PARAM_N_EXPONENT_MAX):
                                        valid_value=False 
                                    elif key=="P" and (value<ScryptCalc.PARAM_P_MIN or value>ScryptCalc.PARAM_P_MAX):
                                        valid_value=False 
                                    elif key=="R" and (value<ScryptCalc.PARAM_R_MIN or value>ScryptCalc.PARAM_R_MAX):
                                        valid_value=False 
                                    elif key=="length" and (value<1 or value>ScryptCalc.PARAM_LENGTH_MAX):
                                        valid_value=False 
                                    elif key=="chain" and (value<1 or value>ScryptCalc.PARAM_CHAIN_MAX):
                                        valid_value=False

                            else:
                                if key=="title":
                                    value=value.strip()
                                    if len(value)>ScryptCalc.PARAM_TITLE_LENGTH_MAX:
                                        value=value[:-(len(value)-ScryptCalc.PARAM_TITLE_LENGTH_MAX)]
                                        value=value.strip()
                                    if len(value)==0:
                                        valid_value=False
                                elif key=="salt" and " " in value:
                                    valid_value=False
                                elif key=="format":
                                    value=value.lower()
                                    if value not in ["hex","bin","base16","base32","base64","base85"]:
                                        valid_value=False
                                elif key in["clearinput","hideinput","hidesalt","hideresult","clearclipboard","nocopy"]:
                                    value=value.lower()
                                    if value in ["1","true","yes"]:
                                        value=True
                                    elif value in ["0","false","no"]:
                                        value=False
                                    else:
                                        valid_value=False
                        else:
                            valid_value=False

                        if valid_value==True:
                            collected_settings[key]=value
                            if set(["title","format","salt","N_exp","P","R","clearinput","hideinput","hidesalt","chain","hideresult","clearclipboard","nocopy"])==set(collected_settings.keys()):
                                break
                                
                    key=ScryptCalc.PURGE_VALUE_RESULT
                    del key
                    key=None
                    value=ScryptCalc.PURGE_VALUE_RESULT
                    del value
                    value=None
            
            while len(settings_lines)>0:
                settings_lines[-1]=ScryptCalc.PURGE_VALUE_RESULT
                settings_lines[-1]=None
                del settings_lines[-1]
                
        for key in ["title","format","salt","N_exp","P","R","length","clearinput","hideinput","hidesalt","chain","hideresult","clearclipboard","nocopy"]:
            if key not in collected_settings:
                collected_settings[key]=None

        input_string=ScryptCalc.PURGE_VALUE_RESULT
        del input_string
        input_string=None
        Cleanup_Memory()

        return collected_settings

    def __init__(self,input_startup_settings_string=u""):
        ScryptCalc.ALTERNATE_PASTE_HOTKEY=ScryptCalc.ALTERNATE_PASTE_HOTKEY.upper()
        self.startup_settings=ScryptCalc.sanitize_settings_string(input_startup_settings_string)
        input_startup_settings_string=ScryptCalc.PURGE_VALUE_RESULT
        del input_startup_settings_string
        input_startup_settings_string=u""
        Cleanup_Memory()
        return

    def flush_std_buffers(self):
        sys.stdout.flush()
        sys.stderr.flush()
        return

    def RUN(self):
        if threading.current_thread().__class__.__name__!="_MainThread":
            raise Exception("ScryptCalc needs to be run from the main thread.")

        UI_Signal=ScryptCalc.UI_Signaller()
        Scrypt_Calculator=ScryptCalc.Scrypt_Calculator(UI_Signal)
        Alternate_Paste_Agent=ScryptCalc.Alternate_Paste_Agent(UI_Signal)
        self.Active_UI=ScryptCalc.UI(UI_Signal,Scrypt_Calculator,Alternate_Paste_Agent,self.startup_settings)
        
        while self.Active_UI.IS_READY()==False:
            time.sleep(ScryptCalc.PENDING_ACTIVITY_HEARTBEAT_SECONDS)

        Scrypt_Calculator.START()
        Alternate_Paste_Agent.START()

        self.main_loop()
        
        Alternate_Paste_Agent.REQUEST_STOP()
        Scrypt_Calculator.REQUEST_STOP()
        Alternate_Paste_Agent.CONCLUDE()
        Scrypt_Calculator.CONCLUDE()
        self.Active_UI.CONCLUDE()
        
        del self.Active_UI
        self.Active_UI=None
        del Alternate_Paste_Agent
        Alternate_Paste_Agent=None
        del Scrypt_Calculator
        Scrypt_Calculator=None
        del UI_Signal
        UI_Signal=None
        return

    def main_loop(self):
        while self.Active_UI.IS_RUNNING()==True:
            time.sleep(ScryptCalc.MAINTHREAD_HEARTBEAT_SECONDS)

            self.flush_std_buffers()
        return


if Versions_Str_Equal_Or_Less(PYQT5_MAX_SUPPORTED_COMPILE_VERSION,PYQT_VERSION_STR)==False:
    sys.stderr.write(f"WARNING: PyQt5 version({PYQT_VERSION_STR}) is higher than the maximum supported version for compiling({PYQT5_MAX_SUPPORTED_COMPILE_VERSION}). The application may run off source code but will fail to compile.\n")
    sys.stderr.flush()

try:
    exe_name=sys.executable.lower().strip().replace(u"/",u"\\").split("\\")[-1].replace(u".exe",u"")
except:
    exe_name=u""

if exe_name==u"python" and sys.argv[0].lower().strip().endswith(u".py"):
    working_directory=os.path.dirname(__file__)
else:
    working_directory=os.path.dirname(sys.executable)

working_directory=os.path.realpath(working_directory)
os.chdir(working_directory)

default_config_file_path=os.path.join(working_directory,u"config.txt")

if len(sys.argv)>1:
    custom_config_file_path=sys.argv[-1].strip()
    if len(custom_config_file_path)>0:
        custom_config_file_path=custom_config_file_path.replace(u"/",u"\\")
        if custom_config_file_path.startswith(u"\\\\")==False and ":" not in custom_config_file_path:
            if custom_config_file_path.startswith(u"\\")==False:
                custom_config_file_path=f"\\{custom_config_file_path}"
            custom_config_file_path=f"{working_directory}{custom_config_file_path}"
else:
    custom_config_file_path=u""

config_string=u""

if len(custom_config_file_path)>0:
    config_string=Get_Config_String_From_File(custom_config_file_path)

if len(config_string)==0:
    config_string=Get_Config_String_From_File(default_config_file_path)

ScryptCalcInstance=ScryptCalc(config_string)

config_string=ScryptCalc.PURGE_VALUE_RESULT
del config_string
config_string=u""

ScryptCalcInstance.RUN()

del ScryptCalcInstance
ScryptCalcInstance=None
Cleanup_Memory()
