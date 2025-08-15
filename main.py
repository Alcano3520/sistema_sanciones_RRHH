# main.py - Sistema RRHH OPTIMIZADO - Interface Responsiva
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import queue
import time
from datetime import datetime
from config import *
from procesador import procesador

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.create_login_window()
    
    def create_login_window(self):
        self.root = tk.Tk()
        self.root.title("Login - Sistema RRHH")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        
        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='white', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Título
        title_label = tk.Label(
            main_frame, 
            text=TITULO_APP,
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=COLOR_PRINCIPAL
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            main_frame, 
            text=f"{EMPRESA} - {VERSION}",
            font=('Arial', 12),
            bg='white',
            fg='gray'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Campos de login
        tk.Label(main_frame, text="Usuario:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        self.usuario_entry = tk.Entry(main_frame, font=('Arial', 12), width=25, relief='solid', bd=1)
        self.usuario_entry.pack(pady=(0, 15), ipady=8)
        
        tk.Label(main_frame, text="Contraseña:", bg='white', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(main_frame, show='*', font=('Arial', 12), width=25, relief='solid', bd=1)
        self.password_entry.pack(pady=(0, 20), ipady=8)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=15)
        
        login_btn = tk.Button(
            btn_frame,
            text="🔐 Ingresar al Sistema",
            command=self.login,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 11, 'bold'),
            width=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=self.root.quit,
            bg='#6c757d',
            fg='white',
            font=('Arial', 11),
            width=12,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(
            main_frame, 
            text="Ingrese sus credenciales de acceso",
            bg='white',
            fg='gray',
            font=('Arial', 10)
        )
        self.status_label.pack(pady=(20, 0))
        
        # Info de usuarios
        info_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='solid', bd=1)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            info_frame,
            text="👥 Usuarios disponibles:",
            bg='#f8f9fa',
            fg='#495057',
            font=('Arial', 9, 'bold')
        ).pack(pady=(8, 5))
        
        for user, pwd in USUARIOS_DEFAULT.items():
            tk.Label(
                info_frame,
                text=f"• {user} / {pwd}",
                bg='#f8f9fa',
                fg='#6c757d',
                font=('Arial', 9)
            ).pack()
        
        tk.Label(info_frame, text="", bg='#f8f9fa').pack(pady=2)
        
        # Eventos
        self.usuario_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus inicial
        self.usuario_entry.focus()
        
        # Iniciar loop
        self.root.mainloop()
    
    def login(self):
        usuario = self.usuario_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not usuario or not password:
            self.status_label.config(text="⚠️ Complete todos los campos", fg=COLOR_ERROR)
            return
        
        self.status_label.config(text="🔄 Validando credenciales...", fg='blue')
        self.root.update()
        
        # Validar en hilo separado para no bloquear UI
        def validar_thread():
            if procesador.validar_usuario(usuario, password):
                self.root.after(0, lambda: self.success_login(usuario))
            else:
                self.root.after(0, lambda: self.status_label.config(text="❌ Usuario o contraseña incorrectos", fg=COLOR_ERROR))
                self.root.after(0, lambda: self.password_entry.delete(0, tk.END))
                self.root.after(0, lambda: self.password_entry.focus())
        
        thread = threading.Thread(target=validar_thread)
        thread.daemon = True
        thread.start()
    
    def success_login(self, usuario):
        self.status_label.config(text="✅ Acceso autorizado", fg='green')
        self.root.update()
        self.root.after(500, lambda: self._complete_login(usuario))
    
    def _complete_login(self, usuario):
        self.root.destroy()
        self.on_login_success(usuario)

class ProgressWindow:
    """⚡ NUEVA: Ventana de progreso mejorada con callbacks en tiempo real"""
    def __init__(self, parent, title="Procesando"):
        self.parent = parent
        self.window = None
        self.progress_var = tk.StringVar()
        self.detail_var = tk.StringVar()
        self.create_window(title)
    
    def create_window(self, title):
        self.window = tk.Toplevel(self.parent)
        self.window.title(title)
        self.window.geometry("500x250")
        self.window.configure(bg='white')
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Centrar
        self.window.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50, 
            self.parent.winfo_rooty() + 50
        ))
        
        frame = tk.Frame(self.window, bg='white', padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(
            frame, 
            text="⚡ Procesando Sanciones",
            bg='white',
            font=('Arial', 16, 'bold'),
            fg=COLOR_PRINCIPAL
        )
        title_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, length=400, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Status principal
        self.status_label = tk.Label(
            frame, 
            textvariable=self.progress_var,
            bg='white',
            font=('Arial', 12, 'bold'),
            fg='#333'
        )
        self.status_label.pack(pady=10)
        
        # Detalles
        self.detail_label = tk.Label(
            frame, 
            textvariable=self.detail_var,
            bg='white',
            font=('Arial', 10),
            fg='#666'
        )
        self.detail_label.pack(pady=5)
        
        # Info adicional
        info_label = tk.Label(
            frame,
            text="💡 Este proceso puede tomar varios segundos\nLa ventana se cerrará automáticamente al finalizar",
            bg='white',
            font=('Arial', 9),
            fg='#999',
            justify=tk.CENTER
        )
        info_label.pack(pady=(20, 0))
        
        self.progress_var.set("Iniciando procesamiento...")
        self.detail_var.set("Preparando sistema...")
    
    def update_progress(self, main_text, detail_text=""):
        """Actualizar progreso desde hilo de trabajo"""
        if self.window and self.window.winfo_exists():
            self.progress_var.set(main_text)
            self.detail_var.set(detail_text)
            self.window.update_idletasks()
    
    def close(self):
        """Cerrar ventana de progreso"""
        if self.window and self.window.winfo_exists():
            self.progress.stop()
            self.window.destroy()

class SancionCheckbox:
    """Clase para manejar checkbox de cada sanción - OPTIMIZADA"""
    def __init__(self, sancion, parent_frame, row, on_selection_change, show_procesado=False):
        self.sancion = sancion
        self.parent_frame = parent_frame
        self.row = row
        self.on_selection_change = on_selection_change
        self.show_procesado = show_procesado
        
        # Variable para el checkbox
        self.is_selected = tk.BooleanVar()
        self.is_selected.trace('w', self.on_check_change)
        
        self.create_row()
    
    def create_row(self):
        """Crear la fila con checkbox y datos"""
        # Frame para la fila completa
        self.row_frame = tk.Frame(self.parent_frame, bg='white', relief='solid', bd=1, height=35)
        self.row_frame.grid(row=self.row, column=0, sticky='ew', padx=1, pady=1)
        self.row_frame.grid_propagate(False)
        
        # Configurar grid
        if self.show_procesado:
            column_widths = [80, 60, 200, 120, 80, 80, 80, 150, 40]
            self._create_procesado_row()
        else:
            column_widths = [40, 80, 60, 200, 120, 80, 150, 40]
            self._create_pendiente_row()
        
        for i, width in enumerate(column_widths):
            self.row_frame.grid_columnconfigure(i, minsize=width, weight=0)
        
        # Color alternado
        bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        self.row_frame.configure(bg=bg_color)
        
        self.update_row_color()
    
    def _create_pendiente_row(self):
        """Crear fila para sanción pendiente"""
        bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        col = 0
        
        # Checkbox
        self.checkbox = tk.Checkbutton(
            self.row_frame,
            variable=self.is_selected,
            bg=bg_color,
            activebackground=bg_color,
            font=('Arial', 10),
            cursor='hand2'
        )
        self.checkbox.grid(row=0, column=col, padx=3, pady=3)
        col += 1
        
        # Datos
        self._create_data_columns(col, bg_color)
        
        # Eventos para seleccionar fila
        clickeable_widgets = [self.row_frame] + [
            child for child in self.row_frame.winfo_children() 
            if isinstance(child, tk.Label)
        ]
        for widget in clickeable_widgets:
            widget.bind('<Button-1>', self.toggle_selection)
    
    def _create_procesado_row(self):
        """Crear fila para sanción procesada"""
        bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        self._create_data_columns(0, bg_color, include_procesado=True)
    
    def _create_data_columns(self, start_col, bg_color, include_procesado=False):
        """Crear columnas de datos"""
        col = start_col
        
        # ID
        id_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('id', '')[:8] + '...',
            bg=bg_color,
            font=('Arial', 8),
            anchor='center'
        )
        id_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
        col += 1
        
        # Código empleado
        cod_label = tk.Label(
            self.row_frame,
            text=str(self.sancion.get('empleado_cod', '')),
            bg=bg_color,
            font=('Arial', 9, 'bold'),
            anchor='center'
        )
        cod_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
        col += 1
        
        # Nombre empleado
        nombre_text = self.sancion.get('empleado_nombre', '')
        if len(nombre_text) > 25:
            nombre_text = nombre_text[:22] + '...'
        
        nombre_label = tk.Label(
            self.row_frame,
            text=nombre_text,
            bg=bg_color,
            font=('Arial', 9),
            anchor='w'
        )
        nombre_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
        col += 1
        
        # Tipo sanción
        tipo_text = self.sancion.get('tipo_sancion', '')
        if len(tipo_text) > 15:
            tipo_text = tipo_text[:12] + '...'
        
        tipo_label = tk.Label(
            self.row_frame,
            text=tipo_text,
            bg=bg_color,
            font=('Arial', 8, 'bold'),
            anchor='center',
            fg=COLOR_SECUNDARIO
        )
        tipo_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
        col += 1
        
        # Fecha
        fecha_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('fecha', '')[:10],
            bg=bg_color,
            font=('Arial', 8),
            anchor='center'
        )
        fecha_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
        col += 1
        
        # Si es procesado, agregar columnas adicionales
        if include_procesado:
            # Procesado por
            procesado_label = tk.Label(
                self.row_frame,
                text=self.sancion.get('procesado_por', 'N/A'),
                bg=bg_color,
                font=('Arial', 8, 'bold'),
                anchor='center',
                fg='green'
            )
            procesado_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
            col += 1
            
            # Fecha procesamiento
            fecha_proc_label = tk.Label(
                self.row_frame,
                text=self.sancion.get('fecha_procesamiento', '')[:10],
                bg=bg_color,
                font=('Arial', 8),
                anchor='center'
            )
            fecha_proc_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
            col += 1
        
        # Observaciones
        obs_text = self.sancion.get('observaciones', '') or ''
        if len(obs_text) > 20:
            obs_text = obs_text[:17] + '...'
        
        obs_label = tk.Label(
            self.row_frame,
            text=obs_text,
            bg=bg_color,
            font=('Arial', 8),
            anchor='w'
        )
        obs_label.grid(row=0, column=col, padx=2, pady=3, sticky='ew')
        col += 1
        
        # Botón detalles
        detalles_btn = tk.Button(
            self.row_frame,
            text="👁️",
            command=self.show_details,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 8),
            width=2,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        detalles_btn.grid(row=0, column=col, padx=2, pady=2)
    
    def on_check_change(self, *args):
        """Callback cuando cambia el estado del checkbox"""
        if not self.show_procesado:
            self.update_row_color()
            self.on_selection_change()
    
    def toggle_selection(self, event=None):
        """Alternar selección al hacer click en la fila"""
        if not self.show_procesado:
            self.is_selected.set(not self.is_selected.get())
    
    def update_row_color(self):
        """Actualizar color de la fila según selección"""
        if not self.show_procesado and self.is_selected.get():
            bg_color = '#d4edda'  # Verde seleccionada
        else:
            bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        
        # Aplicar color
        self.row_frame.configure(bg=bg_color)
        for child in self.row_frame.winfo_children():
            if isinstance(child, (tk.Label, tk.Checkbutton)):
                child.configure(bg=bg_color, activebackground=bg_color)
    
    def show_details(self):
        """Mostrar detalles completos de la sanción"""
        details_window = tk.Toplevel()
        details_window.title(f"Detalles - {self.sancion.get('empleado_nombre', 'N/A')}")
        details_window.geometry("600x500")
        details_window.configure(bg='white')
        details_window.transient(self.row_frame.winfo_toplevel())
        details_window.grab_set()
        
        text_widget = scrolledtext.ScrolledText(
            details_window, 
            wrap=tk.WORD, 
            font=('Courier', 10),
            bg='white',
            padx=15,
            pady=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Contenido optimizado
        content = f"""
📋 DETALLES COMPLETOS DE LA SANCIÓN

🆔 ID: {self.sancion.get('id', 'N/A')}
👤 Empleado: {self.sancion.get('empleado_cod', 'N/A')} - {self.sancion.get('empleado_nombre', 'N/A')}
💼 Puesto: {self.sancion.get('puesto', 'N/A')}
👮 Agente: {self.sancion.get('agente', 'N/A')}
📅 Fecha: {self.sancion.get('fecha', 'N/A')}
🕐 Hora: {self.sancion.get('hora', 'N/A')}
⚠️ Tipo: {self.sancion.get('tipo_sancion', 'N/A')}
📝 Observaciones: {self.sancion.get('observaciones', 'N/A')}
✅ Status: {self.sancion.get('status', 'N/A')}
💬 Comentarios RRHH: {self.sancion.get('comentarios_rrhh', 'PENDIENTE')}
⏰ Creado: {self.sancion.get('created_at', 'N/A')}
🔄 Actualizado: {self.sancion.get('updated_at', 'N/A')}
        """
        
        if self.show_procesado:
            content += f"""
📄 INFORMACIÓN DE PROCESAMIENTO:
👤 Procesado por: {self.sancion.get('procesado_por', 'N/A')}
📅 Fecha procesamiento: {self.sancion.get('fecha_procesamiento', 'N/A')}
⏱️ Tiempo: {self.sancion.get('tiempo_procesamiento', 'N/A')} segundos
            """
        
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        
        close_btn = tk.Button(
            details_window,
            text="Cerrar",
            command=details_window.destroy,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        )
        close_btn.pack(pady=10)

class SancionesTab:
    """⚡ OPTIMIZADA: Pestaña de sanciones con mejor rendimiento"""
    def __init__(self, parent, categoria, sanciones, on_procesar, on_refresh, es_historial=False):
        self.categoria = categoria
        self.sanciones = sanciones
        self.on_procesar = on_procesar
        self.on_refresh = on_refresh
        self.es_historial = es_historial
        self.checkboxes = []
        
        # Para optimización de rendering
        self._render_queue = queue.Queue()
        self._is_rendering = False
        
        self.create_tab(parent)
    
    def create_tab(self, parent):
        """Crear pestaña optimizada"""
        main_frame = tk.Frame(parent, bg='white')
        
        # Header
        header_color = '#28a745' if self.es_historial else COLOR_PRINCIPAL
        header_icon = '📚' if self.es_historial else '📋'
        header_text = f"{header_icon} {self.categoria}"
        if self.es_historial:
            header_text += " - Historial"
        
        header_frame = tk.Frame(main_frame, bg=header_color, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg=header_color)
        title_frame.pack(expand=True, fill=tk.BOTH)
        
        header_label = tk.Label(
            title_frame,
            text=header_text,
            bg=header_color,
            fg='white',
            font=('Arial', 16, 'bold')
        )
        header_label.pack(pady=(15, 5))
        
        count_text = f"{len(self.sanciones)} procesadas" if self.es_historial else f"{len(self.sanciones)} pendientes"
        count_label = tk.Label(
            title_frame,
            text=count_text,
            bg=header_color,
            fg='white',
            font=('Arial', 11)
        )
        count_label.pack()
        
        # Controles
        controls_frame = tk.Frame(main_frame, bg='white')
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        self._create_controls(controls_frame)
        self._create_table_header(main_frame, header_color)
        self._create_scrollable_content(main_frame)
        self._create_footer(main_frame)
        
        # Poblar datos de forma asíncrona para mejor rendimiento
        self.root_frame = main_frame
        self._populate_async()
        
        return main_frame
    
    def _create_controls(self, parent):
        """Crear controles de la pestaña"""
        left_controls = tk.Frame(parent, bg='white')
        left_controls.pack(side=tk.LEFT)
        
        right_controls = tk.Frame(parent, bg='white')
        right_controls.pack(side=tk.RIGHT)
        
        if not self.es_historial:
            # Controles para pendientes
            select_all_btn = tk.Button(
                left_controls,
                text="☑️ Seleccionar Todo",
                command=self.select_all,
                bg=COLOR_SECUNDARIO,
                fg='white',
                font=('Arial', 10, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=15,
                pady=8
            )
            select_all_btn.pack(side=tk.LEFT, padx=(0, 8))
            
            clear_btn = tk.Button(
                left_controls,
                text="🗑️ Limpiar Todo",
                command=self.clear_all,
                bg='#6c757d',
                fg='white',
                font=('Arial', 10),
                relief='flat',
                cursor='hand2',
                padx=15,
                pady=8
            )
            clear_btn.pack(side=tk.LEFT, padx=(0, 15))
            
            self.selected_count_label = tk.Label(
                left_controls,
                text="0 seleccionadas",
                bg='white',
                fg='gray',
                font=('Arial', 10, 'bold')
            )
            self.selected_count_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Botón procesar
            self.process_btn = tk.Button(
                right_controls,
                text="⚡ Procesar Seleccionadas",
                command=self.procesar_seleccionadas,
                bg=COLOR_EXITO,
                fg='white',
                font=('Arial', 11, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=20,
                pady=10,
                state='disabled'
            )
            self.process_btn.pack(side=tk.RIGHT)
        else:
            # Controles para historial
            download_btn = tk.Button(
                left_controls,
                text="📥 Descargar Excel",
                command=self.descargar_excel,
                bg='#17a2b8',
                fg='white',
                font=('Arial', 10, 'bold'),
                relief='flat',
                cursor='hand2',
                padx=15,
                pady=8
            )
            download_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Botón actualizar
        refresh_btn = tk.Button(
            right_controls,
            text="🔄 Actualizar",
            command=self.on_refresh,
            bg='#17a2b8',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
    def _create_table_header(self, parent, header_color):
        """Crear header de tabla"""
        header_table_frame = tk.Frame(parent, bg=header_color, height=40)
        header_table_frame.pack(fill=tk.X, pady=(0, 5))
        header_table_frame.pack_propagate(False)
        
        if self.es_historial:
            headers = ['ID', 'Cód', 'Nombre Empleado', 'Tipo', 'Fecha', 'Proc. Por', 'Fecha Proc.', 'Observaciones', '👁️']
            column_widths = [80, 60, 200, 120, 80, 80, 80, 150, 40]
        else:
            headers = ['☑️', 'ID', 'Cód', 'Nombre Empleado', 'Tipo', 'Fecha', 'Observaciones', '👁️']
            column_widths = [40, 80, 60, 200, 120, 80, 150, 40]
        
        for i, width in enumerate(column_widths):
            header_table_frame.grid_columnconfigure(i, minsize=width, weight=0)
        
        for i, header in enumerate(headers):
            label = tk.Label(
                header_table_frame,
                text=header,
                bg=header_color,
                fg='white',
                font=('Arial', 10, 'bold'),
                anchor='center'
            )
            label.grid(row=0, column=i, padx=1, pady=5, sticky='ew')
    
    def _create_scrollable_content(self, parent):
        """Crear área scrollable optimizada"""
        canvas_frame = tk.Frame(parent, relief='solid', bd=1, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.grid_columnconfigure(0, weight=1, minsize=800)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Eventos optimizados
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_canvas_configure(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.canvas.bind('<Configure>', _on_canvas_configure)
        self.scrollable_frame.bind('<Configure>', _on_frame_configure)
    
    def _create_footer(self, parent):
        """Crear footer informativo"""
        footer_frame = tk.Frame(parent, bg='#f8f9fa', height=35)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        footer_frame.pack_propagate(False)
        
        if self.es_historial:
            footer_text = f"💡 Historial de {self.categoria} | 📥 Usa 'Descargar Excel' para exportar | 👁️ Click para ver detalles"
        else:
            footer_text = f"💡 {len(self.sanciones)} sanciones pendientes | ☑️ Click en filas para seleccionar | ⚡ Procesar seleccionadas"
        
        footer_label = tk.Label(
            footer_frame,
            text=footer_text,
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        footer_label.pack(pady=8)
    
    def _populate_async(self):
        """⚡ NUEVO: Poblar datos de forma asíncrona para mejor rendimiento"""
        def populate_thread():
            try:
                print(f"📊 Poblando {len(self.sanciones)} sanciones en {self.categoria}")
                
                # Crear checkboxes en lotes pequeños para mantener UI responsiva
                batch_size = 20
                for i in range(0, len(self.sanciones), batch_size):
                    batch = self.sanciones[i:i + batch_size]
                    
                    # Programar creación de este lote en UI thread
                    self.root_frame.after(0, self._create_checkbox_batch, batch, i)
                    
                    # Pequeña pausa para mantener UI responsiva
                    time.sleep(0.01)
                
                # Actualizar UI final
                self.root_frame.after(0, self._finalize_population)
                
            except Exception as e:
                print(f"❌ Error poblando pestaña: {e}")
        
        thread = threading.Thread(target=populate_thread)
        thread.daemon = True
        thread.start()
    
    def _create_checkbox_batch(self, batch_sanciones, start_index):
        """Crear un lote de checkboxes"""
        for j, sancion in enumerate(batch_sanciones):
            row_index = start_index + j
            checkbox_row = SancionCheckbox(
                sancion, 
                self.scrollable_frame, 
                row_index, 
                self.update_selected_count if not self.es_historial else lambda: None,
                show_procesado=self.es_historial
            )
            self.checkboxes.append(checkbox_row)
    
    def _finalize_population(self):
        """Finalizar población de datos"""
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        if not self.es_historial:
            self.update_selected_count()
        
        print(f"✅ {len(self.checkboxes)} filas creadas en {self.categoria}")
    
    def select_all(self):
        """Seleccionar todas las sanciones"""
        if not self.es_historial:
            for checkbox in self.checkboxes:
                checkbox.is_selected.set(True)
    
    def clear_all(self):
        """Deseleccionar todas las sanciones"""
        if not self.es_historial:
            for checkbox in self.checkboxes:
                checkbox.is_selected.set(False)
    
    def update_selected_count(self):
        """Actualizar contador de seleccionadas"""
        if self.es_historial:
            return
            
        count = sum(1 for cb in self.checkboxes if cb.is_selected.get())
        self.selected_count_label.config(text=f"{count} seleccionadas")
        
        if count > 0:
            self.process_btn.config(state='normal', bg=COLOR_EXITO)
        else:
            self.process_btn.config(state='disabled', bg='#6c757d')
    
    def procesar_seleccionadas(self):
        """⚡ OPTIMIZADO: Procesar sanciones seleccionadas con validación de concurrencia"""
        if self.es_historial:
            return
            
        sanciones_seleccionadas = [
            cb.sancion for cb in self.checkboxes 
            if cb.is_selected.get()
        ]
        
        if not sanciones_seleccionadas:
            messagebox.showwarning("Advertencia", "No hay sanciones seleccionadas")
            return
        
        # Confirmación con detalles
        respuesta = messagebox.askyesno(
            "Confirmar Procesamiento",
            f"🔄 ¿Procesar {len(sanciones_seleccionadas)} sanciones de '{self.categoria}'?\n\n"
            f"⚡ Sistema optimizado: Procesamiento rápido con validación de concurrencia\n"
            f"💾 Se actualizará el campo 'comentarios_rrhh' en Supabase\n\n"
            f"¿Desea continuar?"
        )
        
        if not respuesta:
            return
        
        self.on_procesar(sanciones_seleccionadas, self.categoria)
    
    def descargar_excel(self):
        """Descargar Excel de esta categoría"""
        if not self.sanciones:
            messagebox.showwarning("Sin datos", "No hay sanciones para descargar")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Historial_{self.categoria.replace(' ', '_')}_{timestamp}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename,
                title="Guardar Excel"
            )
            
            if filepath:
                # Mostrar progreso
                progress = ProgressWindow(self.root_frame.winfo_toplevel(), "Generando Excel")
                
                def export_thread():
                    try:
                        progress.update_progress("Preparando datos...", f"Exportando {len(self.sanciones)} registros")
                        archivo_generado = procesador.exportar_a_excel(self.sanciones, filepath)
                        
                        self.root_frame.after(0, progress.close)
                        
                        if archivo_generado:
                            self.root_frame.after(0, lambda: messagebox.showinfo(
                                "Descarga exitosa", 
                                f"✅ Excel generado exitosamente:\n{filepath}"
                            ))
                            
                            if self.root_frame.after(0, lambda: messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo Excel?")):
                                os.startfile(filepath)
                        else:
                            self.root_frame.after(0, lambda: messagebox.showerror("Error", "No se pudo generar el archivo Excel"))
                    except Exception as e:
                        self.root_frame.after(0, progress.close)
                        self.root_frame.after(0, lambda: messagebox.showerror("Error", f"Error exportando: {e}"))
                
                thread = threading.Thread(target=export_thread)
                thread.daemon = True
                thread.start()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar Excel: {e}")

class MainWindow:
    """⚡ OPTIMIZADA: Ventana principal con mejor rendimiento y concurrencia"""
    def __init__(self, usuario):
        self.usuario = usuario
        self.sanciones_categorizadas = {}
        self.historial_categorizado = {}
        self.root = tk.Tk()
        
        # Queue para comunicación entre threads
        self.update_queue = queue.Queue()
        
        self.setup_main_window()
        self.cargar_datos()
        self.root.mainloop()
    
    def setup_main_window(self):
        """Configurar ventana principal"""
        self.root.title(f"{TITULO_APP} - {self.usuario}")
        self.root.geometry("1400x800")
        self.root.configure(bg='white')
        
        # Maximizar ventana
        try:
            self.root.state('zoomed')  # Windows
        except:
            pass
        
        # Menu bar
        self._create_menu()
        self._create_header()
        self._create_notebook()
        self._create_footer()
    
    def _create_menu(self):
        """Crear barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Sistema
        sistema_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🏠 Sistema", menu=sistema_menu)
        sistema_menu.add_command(label="🔄 Actualizar Datos", command=self.cargar_datos)
        sistema_menu.add_command(label="📊 Estadísticas", command=self.mostrar_estadisticas)
        sistema_menu.add_separator()
        sistema_menu.add_command(label="❌ Salir", command=self.root.quit)
        
        # Menu Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Herramientas", menu=tools_menu)
        tools_menu.add_command(label="🧪 Crear Sanción Prueba", command=self.crear_sancion_prueba)
        tools_menu.add_command(label="🔍 Test Conexión", command=self.test_conexion)
        
        # Menu Reportes
        reportes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Reportes", menu=reportes_menu)
        reportes_menu.add_command(label="📥 Descargar Todo (Excel)", command=self.descargar_todo_excel)
        reportes_menu.add_command(label="📈 Reporte Completo", command=self.generar_reporte_completo)
    
    def _create_header(self):
        """Crear header de la aplicación"""
        header_frame = tk.Frame(self.root, bg=COLOR_PRINCIPAL, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=COLOR_PRINCIPAL)
        header_content.pack(expand=True, fill=tk.BOTH, padx=20)
        
        title_label = tk.Label(
            header_content,
            text=f"🏢 {TITULO_APP}",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=20)
        
        user_frame = tk.Frame(header_content, bg=COLOR_PRINCIPAL)
        user_frame.pack(side=tk.RIGHT, pady=20)
        
        user_label = tk.Label(
            user_frame,
            text=f"👤 Usuario: {self.usuario}",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 12, 'bold')
        )
        user_label.pack(anchor='e')
        
        self.status_label = tk.Label(
            user_frame,
            text="🔄 Sistema optimizado - Listo",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 10)
        )
        self.status_label.pack(anchor='e')
    
    def _create_notebook(self):
        """Crear notebook para pestañas"""
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='white')
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=('Arial', 11, 'bold'))
        
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    def _create_footer(self):
        """Crear footer de la aplicación"""
        footer_frame = tk.Frame(self.root, bg='#f8f9fa', height=40)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        footer_content = tk.Frame(footer_frame, bg='#f8f9fa')
        footer_content.pack(expand=True, fill=tk.BOTH, padx=20)
        
        footer_left = tk.Label(
            footer_content,
            text=f"© {datetime.now().year} {EMPRESA} - {VERSION}",
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        footer_left.pack(side=tk.LEFT, pady=10)
        
        self.footer_right = tk.Label(
            footer_content,
            text=f"🕐 Última actualización: {datetime.now().strftime('%H:%M:%S')}",
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        self.footer_right.pack(side=tk.RIGHT, pady=10)
    
    def cargar_datos(self):
        """⚡ OPTIMIZADO: Cargar datos de forma asíncrona"""
        self.status_label.config(text="🔄 Cargando datos...")
        self.footer_right.config(text="🔄 Actualizando datos...")
        self.root.update()
        
        # Cargar en hilo separado para no bloquear UI
        thread = threading.Thread(target=self._cargar_datos_thread)
        thread.daemon = True
        thread.start()
    
    def _cargar_datos_thread(self):
        """Cargar datos en hilo separado"""
        try:
            # Test conexión
            if not procesador.test_conexion_supabase():
                self.root.after(0, lambda: self.status_label.config(text="❌ Sin conexión"))
                self.root.after(0, lambda: messagebox.showerror("Error", MSG_CONEXION_ERROR))
                return
            
            # Obtener sanciones pendientes (sin doble control)
            sanciones = procesador.obtener_sanciones_pendientes()
            self.sanciones_categorizadas = procesador.categorizar_sanciones(sanciones)
            
            # Obtener historial
            procesadas = procesador.obtener_procesadas_completas()
            self.historial_categorizado = procesador.categorizar_procesadas(procesadas)
            
            # Actualizar UI
            self.root.after(0, self._actualizar_pestañas)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="❌ Error cargando"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error cargando datos: {e}"))
    
    def _actualizar_pestañas(self):
        """Actualizar pestañas con datos cargados"""
        # Limpiar pestañas existentes
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Crear pestañas para pendientes
        for categoria, sanciones in self.sanciones_categorizadas.items():
            tab_obj = SancionesTab(
                self.notebook, 
                categoria, 
                sanciones, 
                self.procesar_sanciones,
                self.cargar_datos,
                es_historial=False
            )
            tab_frame = tab_obj.create_tab(self.notebook)
            
            emoji = {
                "Faltas y Permisos": "📋",
                "Horas y Franco": "⏰", 
                "Resto": "⚠️"
            }.get(categoria, "📄")
            
            self.notebook.add(tab_frame, text=f"{emoji} {categoria} ({len(sanciones)})")
        
        # Crear pestañas para historial
        for categoria, sanciones in self.historial_categorizado.items():
            if sanciones:
                tab_obj = SancionesTab(
                    self.notebook, 
                    categoria, 
                    sanciones, 
                    None,
                    self.cargar_datos,
                    es_historial=True
                )
                tab_frame = tab_obj.create_tab(self.notebook)
                
                emoji = {
                    "Faltas y Permisos": "📚",
                    "Horas y Franco": "📖", 
                    "Resto": "📗"
                }.get(categoria, "📄")
                
                self.notebook.add(tab_frame, text=f"{emoji} H-{categoria} ({len(sanciones)})")
        
        total_pendientes = sum(len(s) for s in self.sanciones_categorizadas.values())
        total_procesadas = sum(len(s) for s in self.historial_categorizado.values())
        
        self.status_label.config(text=f"✅ {total_pendientes} pendientes | {total_procesadas} procesadas")
        self.footer_right.config(text=f"🕐 Actualizado: {datetime.now().strftime('%H:%M:%S')}")
    
    def procesar_sanciones(self, sanciones, categoria):
        """⚡ SÚPER OPTIMIZADO: Procesar sanciones con progreso en tiempo real"""
        if not sanciones:
            return
        
        # Mostrar ventana de progreso
        progress_window = ProgressWindow(self.root, f"Procesando {categoria}")
        
        def procesar_thread():
            try:
                # Callback para actualizar progreso
                def callback_progreso(mensaje):
                    progress_window.update_progress(mensaje, f"Procesando {categoria}")
                
                exitosas, fallidas, errores = procesador.procesar_multiples_sanciones(
                    sanciones, 
                    self.usuario, 
                    callback_progreso
                )
                
                # Cerrar progreso
                self.root.after(0, progress_window.close)
                
                # Mostrar resultado
                if exitosas > 0:
                    mensaje = f"⚡ Procesamiento completado exitosamente\n\n"
                    mensaje += f"🎯 Sanciones procesadas: {exitosas}\n"
                    if fallidas > 0:
                        mensaje += f"❌ Sanciones fallidas: {fallidas}\n"
                    if errores:
                        mensaje += f"\n📝 Errores detectados:\n" + "\n".join(errores[:5])
                    mensaje += f"\n¿Desea descargar un archivo Excel con las sanciones procesadas?"
                    
                    def mostrar_resultado():
                        respuesta = messagebox.askyesno("Procesamiento Exitoso", mensaje)
                        if respuesta:
                            self._descargar_procesadas_recientes(sanciones)
                        self.cargar_datos()
                    
                    self.root.after(0, mostrar_resultado)
                else:
                    mensaje = f"❌ No se pudieron procesar las sanciones\n\n"
                    mensaje += f"Fallidas: {fallidas}\n"
                    if errores:
                        mensaje += f"Errores: {errores[0] if errores else 'Desconocido'}"
                    
                    self.root.after(0, lambda: messagebox.showerror("Error", mensaje))
                    
            except Exception as e:
                self.root.after(0, progress_window.close)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error procesando: {e}"))
        
        thread = threading.Thread(target=procesar_thread)
        thread.daemon = True
        thread.start()
    
    def _descargar_procesadas_recientes(self, sanciones_procesadas):
        """Descargar Excel de sanciones recién procesadas"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Sanciones_Procesadas_{timestamp}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename,
                title="Guardar Sanciones Procesadas"
            )
            
            if filepath:
                # Agregar info de procesamiento
                for sancion in sanciones_procesadas:
                    sancion['procesado_por'] = self.usuario
                    sancion['fecha_procesamiento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                archivo_generado = procesador.exportar_a_excel(sanciones_procesadas, filepath)
                
                if archivo_generado:
                    messagebox.showinfo(
                        "Descarga exitosa", 
                        f"✅ Excel generado exitosamente:\n{filepath}"
                    )
                    
                    if messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo Excel?"):
                        os.startfile(filepath)
                else:
                    messagebox.showerror("Error", "No se pudo generar el archivo Excel")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar Excel: {e}")
    
    def descargar_todo_excel(self):
        """Descargar Excel con todo el historial"""
        try:
            procesadas = procesador.obtener_procesadas_completas()
            
            if not procesadas:
                messagebox.showwarning("Sin datos", "No hay sanciones procesadas para descargar")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Historial_Completo_RRHH_{timestamp}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename,
                title="Guardar Historial Completo"
            )
            
            if filepath:
                # Mostrar progreso
                progress = ProgressWindow(self.root, "Exportando Historial")
                
                def export_thread():
                    try:
                        progress.update_progress("Generando Excel completo...", f"Exportando {len(procesadas)} registros")
                        archivo_generado = procesador.exportar_a_excel(procesadas, filepath)
                        
                        self.root.after(0, progress.close)
                        
                        if archivo_generado:
                            self.root.after(0, lambda: messagebox.showinfo(
                                "Descarga exitosa", 
                                f"✅ Historial completo exportado:\n{filepath}\n\n"
                                f"📊 Total de registros: {len(procesadas)}"
                            ))
                            
                            if self.root.after(0, lambda: messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo Excel?")):
                                os.startfile(filepath)
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Error", "No se pudo generar el archivo Excel"))
                    except Exception as e:
                        self.root.after(0, progress.close)
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Error exportando: {e}"))
                
                thread = threading.Thread(target=export_thread)
                thread.daemon = True
                thread.start()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar historial: {e}")
    
    def generar_reporte_completo(self):
        """Generar reporte completo con estadísticas"""
        def generar_thread():
            try:
                stats = procesador.obtener_estadisticas()
                
                if not stats:
                    self.root.after(0, lambda: messagebox.showwarning("Sin datos", "No se pudieron obtener estadísticas"))
                    return
                
                self.root.after(0, lambda: self._mostrar_reporte(stats))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error generando reporte: {e}"))
        
        thread = threading.Thread(target=generar_thread)
        thread.daemon = True
        thread.start()
    
    def _mostrar_reporte(self, stats):
        """Mostrar ventana de reporte"""
        report_window = tk.Toplevel(self.root)
        report_window.title("📈 Reporte Completo del Sistema")
        report_window.geometry("800x600")
        report_window.configure(bg='white')
        report_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(
            report_window, 
            wrap=tk.WORD, 
            font=('Courier', 10),
            bg='white',
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        total_pendientes = sum(len(s) for s in self.sanciones_categorizadas.values())
        total_procesadas = sum(len(s) for s in self.historial_categorizado.values())
        
        contenido = f"""
📈 REPORTE COMPLETO DEL SISTEMA RRHH OPTIMIZADO
{"="*65}

📊 RESUMEN EJECUTIVO:
{"─"*30}
• Total sanciones pendientes: {total_pendientes}
• Total sanciones procesadas: {total_procesadas}
• Procesadas hoy: {stats.get('procesadas_hoy', 0)}
• Eficiencia: {((total_procesadas/(total_procesadas+total_pendientes))*100):.1f}%

⚡ RENDIMIENTO DEL SISTEMA:
{"─"*30}
• Tiempo promedio por sanción: {stats.get('tiempo_promedio', 0)} segundos
• Tiempo mínimo: {stats.get('tiempo_minimo', 0)} segundos  
• Tiempo máximo: {stats.get('tiempo_maximo', 0)} segundos
• Optimizaciones activas: Threading, Lotes, Validación concurrencia

📋 SANCIONES PENDIENTES POR CATEGORÍA:
{"─"*40}
"""
        
        for categoria, sanciones in self.sanciones_categorizadas.items():
            contenido += f"• {categoria}: {len(sanciones)} pendientes\n"
        
        contenido += f"\n📚 HISTORIAL PROCESADO:\n{'─'*25}\n"
        for categoria, sanciones in self.historial_categorizado.items():
            contenido += f"• {categoria}: {len(sanciones)} procesadas\n"
        
        contenido += f"\n👤 ACTIVIDAD POR USUARIO:\n{'─'*25}\n"
        for usuario, cantidad in stats.get('por_usuario', {}).items():
            contenido += f"• {usuario}: {cantidad} sanciones procesadas\n"
        
        contenido += f"\n🏷️ TIPOS MÁS FRECUENTES:\n{'─'*25}\n"
        for tipo, cantidad in sorted(stats.get('por_tipo', {}).items(), key=lambda x: x[1], reverse=True)[:10]:
            contenido += f"• {tipo}: {cantidad}\n"
        
        contenido += f"""

📅 INFORMACIÓN DEL SISTEMA:
{"─"*30}
• Usuario actual: {self.usuario}
• Fecha de reporte: {datetime.now().strftime('%Y-%m-%d')}
• Hora de generación: {datetime.now().strftime('%H:%M:%S')}
• Versión del sistema: {VERSION}
• Empresa: {EMPRESA}

🔗 ESTADO DE CONEXIONES:
{"─"*30}
• Base remota (Supabase): ✅ Conectado
• Optimizaciones: ✅ Activas
• Control concurrencia: ✅ Habilitado
• Procesamiento por lotes: ✅ Configurado

💡 MEJORAS IMPLEMENTADAS:
{"─"*30}
• ❌ Eliminado doble control de estado
• ⚡ Procesamiento multihilo optimizado  
• 🔒 Validación de concurrencia
• 📊 Progreso en tiempo real
• 🚀 UI responsiva sin bloqueos
        """
        
        text_widget.insert(tk.END, contenido)
        text_widget.config(state=tk.DISABLED)
        
        # Botones
        btn_frame = tk.Frame(report_window, bg='white')
        btn_frame.pack(pady=15)
        
        export_btn = tk.Button(
            btn_frame,
            text="📥 Exportar Reporte",
            command=lambda: self._exportar_reporte(contenido),
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=8
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(
            btn_frame,
            text="Cerrar",
            command=report_window.destroy,
            bg='#6c757d',
            fg='white',
            font=('Arial', 10),
            padx=20,
            pady=8
        )
        close_btn.pack(side=tk.LEFT)
    
    def _exportar_reporte(self, contenido):
        """Exportar reporte a archivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Reporte_RRHH_Optimizado_{timestamp}.txt"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile=filename,
                title="Guardar Reporte"
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                
                messagebox.showinfo(
                    "Reporte exportado", 
                    f"✅ Reporte guardado exitosamente:\n{filepath}"
                )
                
                if messagebox.askyesno("Abrir reporte", "¿Desea abrir el archivo de reporte?"):
                    os.startfile(filepath)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {e}")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas rápidas"""
        def stats_thread():
            try:
                stats = procesador.obtener_estadisticas()
                if stats:
                    self.root.after(0, lambda: self._show_stats_window(stats))
                else:
                    self.root.after(0, lambda: messagebox.showwarning("Advertencia", "No se pudieron obtener estadísticas"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error obteniendo estadísticas: {e}"))
        
        thread = threading.Thread(target=stats_thread)
        thread.daemon = True
        thread.start()
    
    def _show_stats_window(self, stats):
        """Mostrar ventana de estadísticas"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estadísticas del Sistema")
        stats_window.geometry("600x500")
        stats_window.configure(bg='white')
        stats_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(
            stats_window, 
            wrap=tk.WORD, 
            font=('Courier', 11),
            bg='white',
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        contenido = f"""
📊 ESTADÍSTICAS DEL SISTEMA RRHH OPTIMIZADO
{"="*50}

📈 RESUMEN GENERAL:
• Total procesadas: {stats.get('total_procesadas', 0)}
• Procesadas hoy: {stats.get('procesadas_hoy', 0)}

⚡ RENDIMIENTO:
• Tiempo promedio: {stats.get('tiempo_promedio', 0)} segundos
• Tiempo mínimo: {stats.get('tiempo_minimo', 0)} segundos
• Tiempo máximo: {stats.get('tiempo_maximo', 0)} segundos

👤 POR USUARIO:
{"─"*30}
"""
        
        for usuario, cantidad in stats.get('por_usuario', {}).items():
            contenido += f"• {usuario}: {cantidad} sanciones\n"
        
        contenido += f"\n🏷️ POR TIPO DE SANCIÓN:\n{'─'*30}\n"
        for tipo, cantidad in stats.get('por_tipo', {}).items():
            contenido += f"• {tipo}: {cantidad}\n"
        
        contenido += f"""

📅 INFORMACIÓN DE SESIÓN:
{"─"*30}
• Usuario actual: {self.usuario}
• Fecha: {datetime.now().strftime('%Y-%m-%d')}
• Hora: {datetime.now().strftime('%H:%M:%S')}
• Sistema: {VERSION}

🔗 CONEXIÓN:
{"─"*30}
• Estado: ✅ Conectado y optimizado
• Concurrencia: ✅ Habilitada
• Threading: ✅ Activo
        """
        
        text_widget.insert(tk.END, contenido)
        text_widget.config(state=tk.DISABLED)
    
    def crear_sancion_prueba(self):
        """Crear sanción de prueba"""
        def crear_thread():
            try:
                if procesador.crear_sancion_prueba():
                    self.root.after(0, lambda: messagebox.showinfo("Éxito", "✅ Sanción de prueba creada exitosamente"))
                    self.root.after(0, self.cargar_datos)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "❌ No se pudo crear la sanción de prueba"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error creando sanción de prueba: {e}"))
        
        thread = threading.Thread(target=crear_thread)
        thread.daemon = True
        thread.start()
    
    def test_conexion(self):
        """Test de conexión"""
        def test_thread():
            try:
                if procesador.test_conexion_supabase():
                    self.root.after(0, lambda: messagebox.showinfo("Conexión", "✅ Conexión con Supabase exitosa"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Conexión", "❌ Error de conexión con Supabase"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error probando conexión: {e}"))
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()

def main():
    print("🚀 Iniciando Sistema RRHH OPTIMIZADO...")
    print("⚡ Mejoras implementadas:")
    print("   • Eliminado doble control de estado")
    print("   • Procesamiento multihilo")
    print("   • Validación de concurrencia")
    print("   • UI responsiva")
    print("   • Progreso en tiempo real")
    
    def on_login_success(usuario):
        app = MainWindow(usuario)
    
    # Mostrar login
    login = LoginWindow(on_login_success)

if __name__ == "__main__":
    main()
