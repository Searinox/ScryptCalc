import base64,ctypes,gc,os,sys,time,threading,hashlib
from PyQt5.QtCore import (PYQT_VERSION_STR,Qt,QObject,QCoreApplication,pyqtSignal,qInstallMessageHandler,QTimer)
from PyQt5.QtWidgets import (QStyle,QApplication,QMenu,QLabel,QLineEdit,QMainWindow,QPushButton,QSpinBox,QPlainTextEdit,QComboBox,QCheckBox)
from PyQt5.QtGui import (QFont,QTextOption,QTextCursor,QCursor,QKeySequence)

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


class ScryptCalc(object):
    MAINTHREAD_HEARTBEAT_SECONDS=0.1
    PENDING_ACTIVITY_HEARTBEAT_SECONDS=0.1
    CLIPBOARD_SET_TIMEOUT_MILLISECONDS=1000

    COMPUTE_MEMORY_MAX_BYTES=1024**3*2-1

    PARAM_INPUT_MAX=192
    PARAM_SALT_MAX=192
    PARAM_N_EXPONENT_MIN=1
    PARAM_N_EXPONENT_MAX=22
    PARAM_R_MIN=1
    PARAM_R_MAX=128
    PARAM_P_MIN=1
    PARAM_P_MAX=192
    PARAM_LENGTH_MAX=192

    DEFAULTPARAM_N_EXPONENT=18
    DEFAULTPARAM_R=10
    DEFAULTPARAM_P=2
    DEFAULTPARAM_FORMAT="base64"
    DEFAULTPARAM_LENGTH=32

    PURGE_VALUE=u"+"*max(PARAM_INPUT_MAX,PARAM_SALT_MAX,PARAM_LENGTH_MAX)
    PURGE_VALUE_RESULT=u"+"*(PARAM_LENGTH_MAX*8)

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

    class Scrypt_Calculator(object):
        def __init__(self,input_UI_signaller):
            self.UI_signaller=input_UI_signaller
            self.request_exit=threading.Event()
            self.request_exit.clear()
            self.has_quit=threading.Event()
            self.has_quit.clear()
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

        def REQUEST_COMPUTE(self,input_value,input_salt,input_R,input_N,input_P,input_length):
            self.lock_job.acquire()
            self.job={"value":input_value,"salt":input_salt,"R":input_R,"N":input_N,"P":input_P,"length":input_length}
            self.lock_job.release()

            input_value=ScryptCalc.PURGE_VALUE
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
            self.UI_signaller.SEND_EVENT("compute_done",{"result":input_result,"compute_time_ms":input_compute_time_ms})
            input_result=ScryptCalc.PURGE_VALUE
            del input_result
            input_result=None
            input_compute_time_ms=0
            del input_compute_time_ms
            input_compute_time_ms=None
            Cleanup_Memory()
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
                    result=hashlib.scrypt(maxmem=ScryptCalc.COMPUTE_MEMORY_MAX_BYTES,password=value_bytes,salt=salt_bytes,n=new_job["N"],r=new_job["R"],p=new_job["P"],dklen=new_job["length"])
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
                    del new_job
                    new_job={}
                    self.complete_job(result,GetTickCount64()-start_time)
                    result=ScryptCalc.PURGE_VALUE
                    del result
                    result=None
                    Cleanup_Memory()

            self.UI_signaller=None
            Cleanup_Memory()
            self.has_quit.set()
            return

    class UI(object):
        qtmsg_blacklist_startswith=["WARNING: QApplication was not created in the main()","OleSetClipboard: Failed to set mime data (text/plain) on clipboard: COM error"]

        class Text_Editor(QPlainTextEdit):
            def createMimeDataFromSelection(self):
                cursor=self.textCursor()
                start=cursor.selectionStart()
                end=cursor.selectionEnd()
                text=self.document().toRawText()
                selected_text=text[start:end]
                self.parentWidget().set_clipboard_text(selected_text)
                text=ScryptCalc.PURGE_VALUE_RESULT
                del text
                text=None
                start=-1
                end=-1
                selected_text=ScryptCalc.PURGE_VALUE_RESULT
                del selected_text
                selected_text=None
                Cleanup_Memory()
                return None
            
        class Main_Window(QMainWindow):
            def __init__(self,input_parent_app,input_is_ready,input_is_exiting,input_has_quit,input_signaller,input_scrypt_calculator,input_settings):
                super(ScryptCalc.UI.Main_Window,self).__init__(None)

                self.parent_app=input_parent_app
                self.is_exiting=input_is_exiting
                self.has_quit=input_has_quit
                self.UI_signaller=input_signaller
                self.UI_signaller.active_signal.connect(self.signal_response_handler)
                self.scrypt_calculator=input_scrypt_calculator
                self.param_N=-1
                self.memory_used_ok=False
                self.input_enabled=False
                self.waiting_for_result=False

                self.setWindowIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

                self.UI_scale=self.logicalDpiX()/96.0
                self.signal_response_calls={"compute_done":self.receive_result}
                
                self.pending_clipboard_text=None
                
                self.timer_update_clipboard=QTimer(self)
                self.timer_update_clipboard.timeout.connect(self.set_clipboard_text_timer_event)
                self.timer_update_clipboard.setSingleShot(True)

                self.font_arial=QFont("Arial")
                self.font_arial.setPointSize(9)
                self.font_consolas=QFont("Consolas")
                self.font_consolas.setPointSize(10)

                self.setFixedSize(400*self.UI_scale,430*self.UI_scale)
                self.setWindowTitle("ScryptCalc")
                self.setWindowFlags(self.windowFlags()|Qt.MSWindowsFixedSizeDialogHint)

                self.label_input=QLabel(self)
                self.label_input.setGeometry(10*self.UI_scale,5*self.UI_scale,100*self.UI_scale,26*self.UI_scale)
                self.label_input.setText("Input:")
                self.label_input.setFont(self.font_arial)

                self.textbox_input=QLineEdit(self)
                self.textbox_input.setGeometry(10*self.UI_scale,25*self.UI_scale,380*self.UI_scale,26*self.UI_scale)
                self.textbox_input.setFont(self.font_consolas)
                self.textbox_input.setMaxLength(ScryptCalc.PARAM_INPUT_MAX)
                self.textbox_input.setAcceptDrops(False)
                self.textbox_input.setContextMenuPolicy(Qt.CustomContextMenu)

                self.label_salt=QLabel(self)
                self.label_salt.setGeometry(10*self.UI_scale,55*self.UI_scale,100*self.UI_scale,26*self.UI_scale)
                self.label_salt.setText("Salt:")
                self.label_salt.setFont(self.font_arial)

                self.textbox_salt=QLineEdit(self)
                self.textbox_salt.setGeometry(10*self.UI_scale,75*self.UI_scale,380*self.UI_scale,26*self.UI_scale)
                self.textbox_salt.setFont(self.font_consolas)
                self.textbox_salt.setMaxLength(ScryptCalc.PARAM_SALT_MAX)
                self.textbox_salt.setAcceptDrops(False)
                self.textbox_salt.setContextMenuPolicy(Qt.CustomContextMenu)

                self.label_N_exponent=QLabel(self)
                self.label_N_exponent.setGeometry(10*self.UI_scale,115*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_N_exponent.setText("Rounds(N) exponent:")
                self.label_N_exponent.setFont(self.font_arial)

                self.label_N_total=QLabel(self)
                self.label_N_total.setGeometry(240*self.UI_scale,115*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_N_total.setFont(self.font_arial)

                self.label_memory_usage=QLabel(self)
                self.label_memory_usage.setGeometry(240*self.UI_scale,140*self.UI_scale,200*self.UI_scale,26*self.UI_scale)
                self.label_memory_usage.setFont(self.font_arial)

                self.spinbox_N_exponent=QSpinBox(self)
                self.spinbox_N_exponent.setGeometry(165*self.UI_scale,115*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_N_exponent.setRange(ScryptCalc.PARAM_N_EXPONENT_MIN,ScryptCalc.PARAM_N_EXPONENT_MAX)
                self.spinbox_N_exponent.setFont(self.font_arial)
                self.spinbox_N_exponent.setValue(ScryptCalc.DEFAULTPARAM_N_EXPONENT)

                self.label_R=QLabel(self)
                self.label_R.setGeometry(10*self.UI_scale,140*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_R.setText("Memory factor(R):")
                self.label_R.setFont(self.font_arial)

                self.spinbox_R=QSpinBox(self)
                self.spinbox_R.setGeometry(165*self.UI_scale,140*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_R.setRange(ScryptCalc.PARAM_R_MIN,ScryptCalc.PARAM_R_MAX)
                self.spinbox_R.setFont(self.font_arial)
                self.spinbox_R.setValue(ScryptCalc.DEFAULTPARAM_R)

                self.label_P=QLabel(self)
                self.label_P.setGeometry(10*self.UI_scale,165*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_P.setFont(self.font_arial)
                self.label_P.setText("Parallelism factor(P):")

                self.spinbox_P=QSpinBox(self)
                self.spinbox_P.setGeometry(165*self.UI_scale,165*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_P.setRange(ScryptCalc.PARAM_P_MIN,ScryptCalc.PARAM_P_MAX)
                self.spinbox_P.setFont(self.font_arial)
                self.spinbox_P.setValue(ScryptCalc.DEFAULTPARAM_P)

                self.label_length=QLabel(self)
                self.label_length.setGeometry(10*self.UI_scale,190*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_length.setText("Result length(bytes):")
                self.label_length.setFont(self.font_arial)

                self.spinbox_length=QSpinBox(self)
                self.spinbox_length.setGeometry(165*self.UI_scale,190*self.UI_scale,60*self.UI_scale,26*self.UI_scale)
                self.spinbox_length.setRange(1,ScryptCalc.PARAM_LENGTH_MAX)
                self.spinbox_length.setFont(self.font_arial)
                self.spinbox_length.setValue(ScryptCalc.DEFAULTPARAM_LENGTH)

                self.label_result_format=QLabel(self)
                self.label_result_format.setGeometry(10*self.UI_scale,215*self.UI_scale,150*self.UI_scale,26*self.UI_scale)
                self.label_result_format.setText("Result output format:")
                self.label_result_format.setFont(self.font_arial)

                self.combobox_result_format=QComboBox(self)
                self.combobox_result_format.setGeometry(165*self.UI_scale,215*self.UI_scale,100*self.UI_scale,26*self.UI_scale)
                self.combobox_result_format.setFont(self.font_arial)
                self.combobox_result_format.addItem("bin")
                self.combobox_result_format.addItem("hex")
                self.combobox_result_format.addItem("base32")
                self.combobox_result_format.addItem("base64")
                self.combobox_result_format.addItem("base85")
                format_index=self.combobox_result_format.findText(ScryptCalc.DEFAULTPARAM_FORMAT)
                self.combobox_result_format.setCurrentIndex(format_index)

                self.checkbox_clear_password_asap=QCheckBox(self)
                self.checkbox_clear_password_asap.setGeometry(75*self.UI_scale,240*self.UI_scale,250*self.UI_scale,26*self.UI_scale)
                self.checkbox_clear_password_asap.setText("Clear password input field on compute")
                self.checkbox_clear_password_asap.setFont(self.font_arial)

                self.button_compute=QPushButton(self)
                self.button_compute.setGeometry(150*self.UI_scale,267*self.UI_scale,90*self.UI_scale,26*self.UI_scale)
                self.button_compute.setText("Compute")
                self.button_compute.setFont(self.font_arial)

                self.label_result_info=QLabel(self)
                self.label_result_info.setGeometry(40*self.UI_scale,290*self.UI_scale,240*self.UI_scale,26*self.UI_scale)
                self.label_result_info.setText("Result:")
                self.label_result_info.setFont(self.font_arial)

                self.button_copy=QPushButton(self)
                self.button_copy.setGeometry(336*self.UI_scale,341*self.UI_scale,60*self.UI_scale,52*self.UI_scale)
                self.button_copy.setText("Copy\nresult")
                self.button_copy.setFont(self.font_arial)

                self.textedit_result=None
                self.result_bytes=bytes()
                
                self.clipboard=QApplication.clipboard()
                
                self.new_textedit_result_widget()

                if input_settings is not None:
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
                    if input_settings["clear"] is not None:
                        self.checkbox_clear_password_asap.setChecked(input_settings["clear"])
                        input_settings["clear"]=False
                        del input_settings["clear"]
                        input_settings["clear"]=None
                        
                    del input_settings
                    input_settings={}
                
                self.textbox_input.textChanged.connect(self.textbox_input_onchange)
                self.textbox_input.returnPressed.connect(self.begin_compute)
                self.textbox_input.customContextMenuRequested.connect(lambda:ScryptCalc.UI.Main_Window.line_edit_context_menu_show(self.textbox_input))
                self.textbox_salt.textChanged.connect(self.textbox_salt_onchange)
                self.textbox_salt.customContextMenuRequested.connect(lambda:ScryptCalc.UI.Main_Window.line_edit_context_menu_show(self.textbox_salt))
                self.spinbox_N_exponent.valueChanged.connect(self.spinbox_N_exponent_onchange)
                self.spinbox_R.valueChanged.connect(self.spinbox_R_onchange)
                self.combobox_result_format.currentIndexChanged.connect(self.combobox_result_format_onindexchanged)
                self.button_compute.clicked.connect(self.begin_compute)
                self.button_copy.clicked.connect(self.button_copy_onclick)

                self.update_N_param()
                self.update_memory_usage()
                self.set_input_enabled(True)
                
                Cleanup_Memory()
                input_is_ready.set()
                return
            
            def set_clipboard_text(self,input_text):
                self.timer_update_clipboard.start(0)
                self.pending_clipboard_text=input_text
                input_text=ScryptCalc.PURGE_VALUE_RESULT
                del input_text
                input_text=None
                Cleanup_Memory()
                return
            
            def set_clipboard_text_timer_event(self):
                if self.pending_clipboard_text is None:
                    return
                
                start_time=GetTickCount64()
                while self.clipboard.text()!=self.pending_clipboard_text and (GetTickCount64()-start_time)<ScryptCalc.CLIPBOARD_SET_TIMEOUT_MILLISECONDS:
                    self.clipboard.setText(self.pending_clipboard_text)
                    QCoreApplication.processEvents()
                self.pending_clipboard_text=ScryptCalc.PURGE_VALUE_RESULT
                del self.pending_clipboard_text
                self.pending_clipboard_text=None
                Cleanup_Memory()
                return
            
            def new_textedit_result_widget(self):
                if self.textedit_result is not None:
                    enabled_state=self.textedit_result.isEnabled()
                    self.setUpdatesEnabled(False)
                    self.textedit_result.hide()
                    cursor=self.textedit_result.textCursor()
                    cursor.movePosition(QTextCursor.End)
                    self.textedit_result.setTextCursor(cursor)
                    del cursor
                    cursor=None
                    self.textedit_result.document().clearUndoRedoStacks()
                    self.textedit_result.document().setPlainText(ScryptCalc.PURGE_VALUE_RESULT)
                    self.textedit_result.document().setPlainText(u"")
                    self.textedit_result.document().clear()
                    self.textedit_result.setDocument(None)
                    self.textedit_result.setParent(None)
                    self.textedit_result.destroy()
                    del self.textedit_result
                    self.textedit_result=None
                    Cleanup_Memory()
                else:
                    enabled_state=True

                self.textedit_result=ScryptCalc.UI.Text_Editor(self)
                self.textedit_result.setAttribute(Qt.WA_DeleteOnClose,True) 
                self.textedit_result.setReadOnly(True)
                self.textedit_result.setGeometry(5*self.UI_scale,314*self.UI_scale,328*self.UI_scale,110*self.UI_scale)
                self.textedit_result.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                self.textedit_result.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.textedit_result.verticalScrollBar().setStyleSheet(f"QScrollBar:vertical {chr(123)}border:{str(round(1*self.UI_scale))}px; width:{str(round(15*self.UI_scale))}px solid;{chr(125)}")
                self.textedit_result.setFont(self.font_consolas)
                self.textedit_result.setWordWrapMode(QTextOption.WrapAnywhere)
                self.textedit_result.setUndoRedoEnabled(False)
                document=self.textedit_result.document()
                document.setUndoRedoEnabled(False)
                document.setUseDesignMetrics(False)
                document.setMaximumBlockCount(0)
                self.textedit_result.setAcceptDrops(False)
                
                self.textedit_result.setEnabled(enabled_state)
                self.textedit_result.show()
                self.setUpdatesEnabled(True)
                enabled_state=False
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

            def combobox_result_format_onindexchanged(self):
                self.display_result()
                return

            def set_input_enabled(self,input_state):
                if input_state!=self.input_enabled:
                    self.input_enabled=input_state
                    self.textedit_result.setEnabled(input_state)
                    self.textbox_input.setEnabled(input_state)
                    self.textbox_salt.setEnabled(input_state)
                    self.spinbox_length.setEnabled(input_state)
                    self.spinbox_N_exponent.setEnabled(input_state)
                    self.spinbox_R.setEnabled(input_state)
                    self.spinbox_P.setEnabled(input_state)
                    self.combobox_result_format.setEnabled(input_state)
                    self.checkbox_clear_password_asap.setEnabled(input_state)
                    self.update_button_state()
                return

            def update_button_state(self):
                self.button_compute.setEnabled(self.input_enabled and self.memory_used_ok)
                result_text=self.textedit_result.document().toRawText()
                result_not_empty=len(result_text)>0
                result_text=ScryptCalc.PURGE_VALUE_RESULT
                del result_text
                result_text=None
                Cleanup_Memory()
                self.button_copy.setEnabled(self.input_enabled and result_not_empty)
                result_not_empty=False
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

            def begin_compute(self):
                if self.button_compute.isEnabled()==False:
                    return

                self.set_input_enabled(False)
                self.new_textedit_result_widget()
                self.purge_result_info()
                self.waiting_for_result=True
                self.label_result_info.setText("Computing result...")
                self.scrypt_calculator.REQUEST_COMPUTE(self.textbox_input.text(),self.textbox_salt.text(),self.spinbox_R.value(),self.param_N,self.spinbox_P.value(),self.spinbox_length.value())

                if self.checkbox_clear_password_asap.isChecked()==True:
                    ScryptCalc.UI.Main_Window.purge_textbox_data(self.textbox_input)
                return
            
            def button_copy_onclick(self):
                result_text=self.textedit_result.document().toRawText()
                self.set_clipboard_text(result_text)
                result_text=ScryptCalc.PURGE_VALUE_RESULT
                del result_text
                result_text=None
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

            def closeEvent(self,event):
                if self.is_exiting.is_set()==True or self.waiting_for_result==True:
                    event.ignore()
                    return

                self.is_exiting.set()
                
                self.purge_result_bytes()
                self.new_textedit_result_widget()
                ScryptCalc.UI.Main_Window.purge_textbox_data(self.textbox_input)
                ScryptCalc.UI.Main_Window.purge_textbox_data(self.textbox_salt)
                self.purge_result_info()
                self.spinbox_N_exponent.setValue(1)
                self.spinbox_R.setValue(1)
                self.spinbox_P.setValue(1)
                self.spinbox_length.setValue(1)
                self.textbox_input.setParent(None)
                self.textbox_input.destroy()
                del self.textbox_input
                self.textbox_input=None
                self.textbox_salt.setParent(None)
                self.textbox_salt.destroy()
                del self.textbox_salt
                self.textbox_salt=None
                self.combobox_result_format.setCurrentIndex(1)
                QCoreApplication.processEvents()
                self.UI_signaller=None
                self.parent_app=None
                Cleanup_Memory()
                self.has_quit.set()
                return

            def receive_result(self,result_data):
                self.result_bytes=result_data["result"]
                self.label_result_info.setText(f"Result took {round(result_data['compute_time_ms']/1000.0,3)} second(s):")
                result_data["result"]=ScryptCalc.PURGE_VALUE
                del result_data["result"]
                result_data["result"]=None
                result_data["compute_time_ms"]=ScryptCalc.PURGE_VALUE
                del result_data["compute_time_ms"]
                result_data["compute_time_ms"]=None
                del result_data
                result_data={}
                Cleanup_Memory()
                self.set_input_enabled(True)
                self.waiting_for_result=False
                self.display_result()
                self.button_copy.setFocus()
                self.parent_app.alert(self)
                return

            def display_result(self):
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

                self.textedit_result.document().setPlainText(text_value)
                text_value=ScryptCalc.PURGE_VALUE_RESULT
                del text_value
                text_value=None
                Cleanup_Memory()
                self.update_button_state()
                return

            def purge_result_info(self):
                self.label_result_info.setText(ScryptCalc.PURGE_VALUE_RESULT)
                self.label_result_info.setText(u"")
                Cleanup_Memory()
                return

            def purge_result_bytes(self):
                self.result_bytes=bytes(ScryptCalc.PURGE_VALUE,"utf-8")
                del self.result_bytes
                self.result_bytes=bytes()
                Cleanup_Memory()
                return

            @staticmethod
            def purge_textbox_data(input_textbox):
                input_textbox.deselect()
                input_textbox.setSelection(0,0)
                input_textbox.setCursorPosition(0)
                max_length=input_textbox.maxLength()
                input_textbox.setMaxLength(0)
                input_textbox.clear()
                input_textbox.setMaxLength(max_length)
                max_length=-1
                input_textbox.setText(ScryptCalc.PURGE_VALUE)
                input_textbox.setSelection(0,0)
                input_textbox.setCursorPosition(0)
                input_textbox.setText(u"")
                Cleanup_Memory()
                return

            @staticmethod
            def line_edit_context_menu_show(source_item):
                parent=source_item.parentWidget()
                clipboard=parent.clipboard
                
                menu=QMenu(parent)
                item_text_length=len(source_item.text())
                if item_text_length>0:
                    menu_action=menu.addAction("Select &All")
                    menu_action.setShortcut(QKeySequence(Qt.Key_A))
                    menu_action.triggered.connect(lambda:source_item.selectAll())
                    if source_item.hasSelectedText()==True:
                        menu.addSeparator()
                        menu_action=menu.addAction("&Copy Selection")
                        menu_action.setShortcut(QKeySequence(Qt.Key_C))
                        menu_action.triggered.connect(lambda:parent.set_clipboard_text(source_item.selectedText()))
                        menu_action=menu.addAction("Cu&t Selection")
                        menu_action.setShortcut(QKeySequence(Qt.Key_T))
                        menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.line_edit_context_menu_cut_selection(parent,source_item))
                        menu_action=menu.addAction("&Delete Selection")
                        menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.line_edit_context_menu_delete_selection(source_item))
                        menu_action.setShortcut(QKeySequence(Qt.Key_D))
                        menu.addSeparator()
                        menu_action=menu.addAction("D&eselect")
                        menu_action.triggered.connect(lambda:source_item.deselect())
                        menu_action.setShortcut(QKeySequence(Qt.Key_E))
                if len(clipboard.text())>0:
                    if source_item.hasSelectedText()==True:
                        menu_action=menu.addAction("&Paste Over Selection")
                        menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.line_edit_context_menu_paste_over_selection(source_item,clipboard))
                    else:
                        menu_action=menu.addAction("&Paste")
                        menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.line_edit_context_menu_paste(source_item,clipboard))
                    menu_action.setShortcut(QKeySequence(Qt.Key_P))
                if item_text_length>0:
                    menu.addSeparator()
                    menu_action=menu.addAction("Clea&r")
                    menu_action.setShortcut(QKeySequence(Qt.Key_R))
                    menu_action.triggered.connect(lambda:ScryptCalc.UI.Main_Window.purge_textbox_data(source_item))
                    
                item_text_length=-1
                if len(menu.actions())>0:
                    menu.exec_(QCursor.pos())
                    
                while len(menu.actions())>0:
                    action=menu.actions()[0]
                    menu.removeAction(action)
                    action.deleteLater()
                    del action
                    action=None
                menu.deleteLater()
                del menu
                menu=None
                Cleanup_Memory()
                source_item.setFocus()
                return
        
            @staticmethod
            def line_edit_context_menu_cut_selection(parent,source_item):
                parent.set_clipboard_text(source_item.selectedText())
                old_position=source_item.cursorPosition()
                source_item.setText(f"{source_item.text()[:source_item.selectionStart()]}{source_item.text()[source_item.selectionEnd():]}")
                source_item.setCursorPosition(old_position)
                return
    
            @staticmethod
            def line_edit_context_menu_delete_selection(source_item):
                old_selection_start=source_item.selectionStart()
                source_item.setText(f"{source_item.text()[:source_item.selectionStart()]}{source_item.text()[source_item.selectionEnd():]}")
                source_item.setCursorPosition(old_selection_start)
                return
    
            @staticmethod
            def line_edit_context_menu_paste_over_selection(source_item,clipboard):
                old_selection_start=source_item.selectionStart()
                source_item.setText(f"{source_item.text()[:source_item.selectionStart()]}{clipboard.text()}{source_item.text()[source_item.selectionEnd():]}")
                source_item.setCursorPosition(old_selection_start+len(clipboard.text()))
                return
    
            @staticmethod
            def line_edit_context_menu_paste(source_item,clipboard):
                old_position=source_item.cursorPosition()
                source_item.setText(f"{source_item.text()[:source_item.cursorPosition()]}{clipboard.text()}{source_item.text()[source_item.cursorPosition():]}")
                source_item.setCursorPosition(old_position+len(clipboard.text()))
                return

        def __init__(self,input_signaller,input_scrypt_calculator,input_settings=None):
            qInstallMessageHandler(self.qtmsg_handler)
            self.is_ready=threading.Event()
            self.is_ready.clear()
            self.is_exiting=threading.Event()
            self.is_exiting.clear()
            self.has_quit=threading.Event()
            self.has_quit.clear()
            self.UI_signaller=input_signaller
            self.scrypt_calculator=input_scrypt_calculator
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
            self.UI_app.setStyle("fusion")
            self.UI_window=ScryptCalc.UI.Main_Window(self.UI_app,self.is_ready,self.is_exiting,self.has_quit,self.UI_signaller,self.scrypt_calculator,self.startup_settings)
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

        if input_string is not None:
            try:
                settings_lines=[line.strip() for line in input_string.split("\n") if line.strip()]
            except:
                settings_lines=[input_string]

            for line in settings_lines:
                separator_pos=line.find("=")
                if separator_pos>-1:
                    key=line[:separator_pos].lower().strip()
                    value=line[separator_pos+1:].strip()
                    if key in ["format","salt","nexp","p","r","length","clear"]:
                        if key=="nexp":
                            key="N_exp"
                        if key in ["p", "r"]:
                            key=key.upper()

                        valid_value=True

                        if len(value)>0 and len(value)<=ScryptCalc.PARAM_SALT_MAX:
                            if key in ["N_exp","P","R","length"]:
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

                            else:
                                if key=="salt" and " " in value:
                                    valid_value=False
                                elif key=="format":
                                    value=value.lower()
                                    if value not in ["hex","bin","base16","base32","base64","base85"]:
                                        valid_value=False
                                elif key=="clear":
                                    value=value.lower()
                                    if value in ["1", "true", "yes"]:
                                        value=True
                                    elif value in ["0", "false", "no"]:
                                        value=False
                                    else:
                                        valid_value=False
                        else:
                            valid_value=False

                        if valid_value==True:
                            collected_settings[key]=value
                            if set(["format","salt","N_exp","P","R","clear"])==set(collected_settings.keys()):
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
                
        for key in ["format","salt","N_exp","P","R","length","clear"]:
            if key not in collected_settings:
                collected_settings[key]=None

        input_string=ScryptCalc.PURGE_VALUE_RESULT
        del input_string
        input_string=None
        Cleanup_Memory()

        return collected_settings

    def __init__(self,input_startup_settings_string=None):
        self.startup_settings=ScryptCalc.sanitize_settings_string(input_startup_settings_string)
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
        self.Active_UI=ScryptCalc.UI(UI_Signal,Scrypt_Calculator,self.startup_settings)
        
        while self.Active_UI.IS_READY()==False:
            time.sleep(ScryptCalc.PENDING_ACTIVITY_HEARTBEAT_SECONDS)

        Scrypt_Calculator.START()

        self.main_loop()
        
        Scrypt_Calculator.REQUEST_STOP()
        Scrypt_Calculator.CONCLUDE()
        self.Active_UI.CONCLUDE()
        
        del self.Active_UI
        self.Active_UI=None
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

config_file_path=os.path.join(os.path.realpath(os.path.dirname(sys.executable)),"config.txt")

try:
    with open(config_file_path,"r") as file_handle:
        file_handle.seek(0,2)
        file_size=file_handle.tell()
        file_handle.seek(0,0)
        if file_size<=768:
            config_string=file_handle.read()
        else:
            config_string=None
        config_string=str(config_string)
except:
    config_string=None

ScryptCalcInstance=ScryptCalc(config_string)
config_string=ScryptCalc.PURGE_VALUE_RESULT
del config_string
config_string=None
ScryptCalcInstance.RUN()

del ScryptCalcInstance
ScryptCalcInstance=None
Cleanup_Memory()
