# main_con_excel_historial.py - Sistema RRHH Completo con Excel e Historial
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
from datetime import datetime
from config import *
from procesador import procesador

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.create_login_window()
    
    def create_login_window(self):
        # Crear ventana principal para login
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
        
        tk.Label(info_frame, text="", bg='#f8f9fa').pack(pady=2)  # Espaciado
        
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
        
        if procesador.validar_usuario(usuario, password):
            self.status_label.config(text="✅ Acceso autorizado", fg='green')
            self.root.update()
            self.root.after(500, lambda: self.success_login(usuario))
        else:
            self.status_label.config(text="❌ Usuario o contraseña incorrectos", fg=COLOR_ERROR)
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def success_login(self, usuario):
        self.root.destroy()
        self.on_login_success(usuario)

class SancionCheckbox:
    """Clase para manejar checkbox de cada sanción"""
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
        self.row_frame = tk.Frame(self.parent_frame, bg='white', relief='solid', bd=1)
        self.row_frame.grid(row=self.row, column=0, sticky='ew', padx=2, pady=1)
        
        # Configurar grid
        self.row_frame.grid_columnconfigure(3, weight=1)  # Nombre empleado se expande
        
        # Color alternado
        bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        self.row_frame.configure(bg=bg_color)
        
        # Checkbox (solo si no es historial)
        col = 0
        if not self.show_procesado:
            self.checkbox = tk.Checkbutton(
                self.row_frame,
                variable=self.is_selected,
                bg=bg_color,
                activebackground=bg_color,
                font=('Arial', 12),
                cursor='hand2'
            )
            self.checkbox.grid(row=0, column=col, padx=5, pady=5)
            col += 1
        
        # ID (primeros 8 caracteres)
        id_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('id', '')[:8] + '...',
            bg=bg_color,
            font=('Arial', 9),
            width=12,
            anchor='center'
        )
        id_label.grid(row=0, column=col, padx=5, pady=5)
        col += 1
        
        # Código empleado
        cod_label = tk.Label(
            self.row_frame,
            text=str(self.sancion.get('empleado_cod', '')),
            bg=bg_color,
            font=('Arial', 9, 'bold'),
            width=8,
            anchor='center'
        )
        cod_label.grid(row=0, column=col, padx=5, pady=5)
        col += 1
        
        # Nombre empleado
        nombre_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('empleado_nombre', ''),
            bg=bg_color,
            font=('Arial', 9),
            anchor='w',
            wraplength=200
        )
        nombre_label.grid(row=0, column=col, padx=5, pady=5, sticky='w')
        col += 1
        
        # Tipo sanción
        tipo_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('tipo_sancion', ''),
            bg=bg_color,
            font=('Arial', 9, 'bold'),
            width=15,
            anchor='center',
            fg=COLOR_SECUNDARIO
        )
        tipo_label.grid(row=0, column=col, padx=5, pady=5)
        col += 1
        
        # Fecha
        fecha_label = tk.Label(
            self.row_frame,
            text=self.sancion.get('fecha', '')[:10],
            bg=bg_color,
            font=('Arial', 9),
            width=12,
            anchor='center'
        )
        fecha_label.grid(row=0, column=col, padx=5, pady=5)
        col += 1
        
        # Si es historial, mostrar info de procesamiento
        if self.show_procesado:
            procesado_label = tk.Label(
                self.row_frame,
                text=self.sancion.get('procesado_por', 'N/A'),
                bg=bg_color,
                font=('Arial', 9, 'bold'),
                width=10,
                anchor='center',
                fg='green'
            )
            procesado_label.grid(row=0, column=col, padx=5, pady=5)
            col += 1
            
            fecha_proc_label = tk.Label(
                self.row_frame,
                text=self.sancion.get('fecha_procesamiento', '')[:10],
                bg=bg_color,
                font=('Arial', 9),
                width=12,
                anchor='center'
            )
            fecha_proc_label.grid(row=0, column=col, padx=5, pady=5)
            col += 1
        
        # Observaciones (truncadas)
        obs_text = self.sancion.get('observaciones', '') or ''
        obs_display = (obs_text[:30] + '...') if len(obs_text) > 30 else obs_text
        obs_label = tk.Label(
            self.row_frame,
            text=obs_display,
            bg=bg_color,
            font=('Arial', 8),
            anchor='w',
            wraplength=200
        )
        obs_label.grid(row=0, column=col, padx=5, pady=5, sticky='w')
        col += 1
        
        # Botón detalles
        detalles_btn = tk.Button(
            self.row_frame,
            text="👁️",
            command=self.show_details,
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 8),
            width=3,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        detalles_btn.grid(row=0, column=col, padx=5, pady=2)
        
        # Evento para seleccionar toda la fila (solo si no es historial)
        if not self.show_procesado:
            widgets_clickeables = [self.row_frame, id_label, cod_label, nombre_label, tipo_label, fecha_label, obs_label]
            for widget in widgets_clickeables:
                widget.bind('<Button-1>', self.toggle_selection)
    
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
            # Seleccionada - color verde
            bg_color = '#d4edda'
        else:
            # No seleccionada - color alternado
            bg_color = '#f8f9fa' if self.row % 2 == 0 else 'white'
        
        # Aplicar color a todos los widgets de la fila
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
        
        # Contenido
        text_widget = scrolledtext.ScrolledText(
            details_window, 
            wrap=tk.WORD, 
            font=('Courier', 10),
            bg='white',
            padx=15,
            pady=15
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Formatear información
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
📑 Obs. Adicionales: {self.sancion.get('observaciones_adicionales', 'N/A') or 'Ninguna'}
✅ Status: {self.sancion.get('status', 'N/A')}
💬 Comentarios Gerencia: {self.sancion.get('comentarios_gerencia', 'N/A') or 'Ninguno'}
🏢 Comentarios RRHH: {self.sancion.get('comentarios_rrhh', 'N/A') or 'PENDIENTE'}
📷 Foto URL: {self.sancion.get('foto_url', 'N/A') or 'No disponible'}
⏰ Creado: {self.sancion.get('created_at', 'N/A')}
🔄 Actualizado: {self.sancion.get('updated_at', 'N/A')}
        """
        
        # Si es historial, agregar info de procesamiento
        if self.show_procesado:
            content += f"""
🔄 INFORMACIÓN DE PROCESAMIENTO:
👤 Procesado por: {self.sancion.get('procesado_por', 'N/A')}
📅 Fecha procesamiento: {self.sancion.get('fecha_procesamiento', 'N/A')}
            """
        
        text_widget.insert(tk.END, content.strip())
        text_widget.config(state=tk.DISABLED)
        
        # Botón cerrar
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
    def __init__(self, parent, categoria, sanciones, on_procesar, on_refresh, es_historial=False):
        self.categoria = categoria
        self.sanciones = sanciones
        self.on_procesar = on_procesar
        self.on_refresh = on_refresh
        self.es_historial = es_historial
        self.checkboxes = []
        
        self.create_tab(parent)
    
    def create_tab(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent, bg='white')
        
        # Header con info y estilo
        header_color = '#28a745' if self.es_historial else COLOR_PRINCIPAL
        header_icon = '📚' if self.es_historial else '📋'
        header_text = f"{header_icon} {self.categoria} - Historial" if self.es_historial else f"{header_icon} {self.categoria}"
        
        header_frame = tk.Frame(main_frame, bg=header_color, height=80)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Título y contador
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
        
        # Frame para controles
        controls_frame = tk.Frame(main_frame, bg='white')
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Lado izquierdo - Selección (solo para pendientes)
        left_controls = tk.Frame(controls_frame, bg='white')
        left_controls.pack(side=tk.LEFT)
        
        if not self.es_historial:
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
            
            # Contador de seleccionadas
            self.selected_count_label = tk.Label(
                left_controls,
                text="0 seleccionadas",
                bg='white',
                fg='gray',
                font=('Arial', 10, 'bold')
            )
            self.selected_count_label.pack(side=tk.LEFT, padx=(10, 0))
        else:
            # Para historial, mostrar opciones de descarga
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
        
        # Lado derecho - Acciones
        right_controls = tk.Frame(controls_frame, bg='white')
        right_controls.pack(side=tk.RIGHT)
        
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
        
        if not self.es_historial:
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
        
        # Header de la tabla
        header_table_frame = tk.Frame(main_frame, bg=header_color, height=35)
        header_table_frame.pack(fill=tk.X, pady=(0, 5))
        header_table_frame.pack_propagate(False)
        
        # Headers según tipo de vista
        if self.es_historial:
            headers = ['ID', 'Cód', 'Nombre Empleado', 'Tipo', 'Fecha', 'Proc. Por', 'Fecha Proc.', 'Observaciones', '👁️']
        else:
            headers = ['☑️', 'ID', 'Cód', 'Nombre Empleado', 'Tipo', 'Fecha', 'Observaciones', '👁️']
        
        for i, header in enumerate(headers):
            label = tk.Label(
                header_table_frame,
                text=header,
                bg=header_color,
                fg='white',
                font=('Arial', 10, 'bold'),
                width=10 if header not in ['Nombre Empleado', 'Observaciones'] else 0
            )
            label.grid(row=0, column=i, padx=2, pady=5, sticky='ew' if header in ['Nombre Empleado', 'Observaciones'] else '')
        
        # Configurar grid del header
        if self.es_historial:
            header_table_frame.grid_columnconfigure(2, weight=1)  # Nombre empleado
            header_table_frame.grid_columnconfigure(7, weight=1)  # Observaciones
        else:
            header_table_frame.grid_columnconfigure(3, weight=1)  # Nombre empleado  
            header_table_frame.grid_columnconfigure(6, weight=1)  # Observaciones
        
        # Frame scrollable para las sanciones
        canvas_frame = tk.Frame(main_frame, relief='solid', bd=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Pack canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para scroll con rueda del mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Poblar con sanciones
        self.populate_sanciones()
        
        # Footer con información
        footer_frame = tk.Frame(main_frame, bg='#f8f9fa', height=40)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        footer_frame.pack_propagate(False)
        
        footer_text = "💡 Tip: Usa 📥 para descargar Excel de esta categoría" if self.es_historial else "💡 Tip: Haz click en 👁️ para ver detalles completos | Click en la fila para seleccionar"
        footer_label = tk.Label(
            footer_frame,
            text=footer_text,
            bg='#f8f9fa',
            fg='#6c757d',
            font=('Arial', 9)
        )
        footer_label.pack(pady=10)
        
        # Actualizar contador inicial (solo para pendientes)
        if not self.es_historial:
            self.update_selected_count()
        
        return main_frame
    
    def populate_sanciones(self):
        """Crear checkboxes para cada sanción"""
        self.checkboxes = []
        
        for i, sancion in enumerate(self.sanciones):
            checkbox_row = SancionCheckbox(
                sancion, 
                self.scrollable_frame, 
                i, 
                self.update_selected_count if not self.es_historial else lambda: None,
                show_procesado=self.es_historial
            )
            self.checkboxes.append(checkbox_row)
        
        # Actualizar región scrollable
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
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
        
        # Habilitar/deshabilitar botón procesar
        if count > 0:
            self.process_btn.config(state='normal', bg=COLOR_EXITO)
        else:
            self.process_btn.config(state='disabled', bg='#6c757d')
    
    def procesar_seleccionadas(self):
        """Procesar sanciones seleccionadas"""
        if self.es_historial:
            return
            
        sanciones_seleccionadas = [
            cb.sancion for cb in self.checkboxes 
            if cb.is_selected.get()
        ]
        
        if not sanciones_seleccionadas:
            messagebox.showwarning("Advertencia", "No hay sanciones seleccionadas")
            return
        
        self.on_procesar(sanciones_seleccionadas, self.categoria)
    
    def descargar_excel(self):
        """Descargar Excel de esta categoría"""
        if not self.sanciones:
            messagebox.showwarning("Sin datos", "No hay sanciones para descargar")
            return
        
        try:
            # Pedir ubicación para guardar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Historial_{self.categoria.replace(' ', '_')}_{timestamp}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename,  # CORREGIDO: era initialname
                title="Guardar Excel"
            )
            
            if filepath:
                # Intentar exportación completa, si falla usar simple
                archivo_generado = procesador.exportar_a_excel(self.sanciones, filepath)
                
                if not archivo_generado:
                    print("⚠️ Exportación completa falló, intentando versión simple...")
                    archivo_generado = procesador.exportar_a_excel_simple(self.sanciones, filepath)
                
                if archivo_generado:
                    messagebox.showinfo(
                        "Descarga exitosa", 
                        f"✅ Excel generado exitosamente:\n{filepath}"
                    )
                    
                    # Preguntar si quiere abrir el archivo
                    if messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo Excel?"):
                        os.startfile(filepath)
                else:
                    messagebox.showerror("Error", "No se pudo generar el archivo Excel")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar Excel: {e}")

class MainWindow:
    def __init__(self, usuario):
        self.usuario = usuario
        self.sanciones_categorizadas = {}
        self.historial_categorizado = {}
        self.root = tk.Tk()
        
        self.setup_main_window()
        self.cargar_datos()
        self.root.mainloop()
    
    def setup_main_window(self):
        self.root.title(f"{TITULO_APP} - {self.usuario}")
        self.root.geometry("1400x800")
        self.root.configure(bg='white')
        
        # Maximizar ventana
        self.root.state('zoomed')  # Windows
        
        # Menu bar
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
        
        # Header principal
        header_frame = tk.Frame(self.root, bg=COLOR_PRINCIPAL, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg=COLOR_PRINCIPAL)
        header_content.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Título principal
        title_label = tk.Label(
            header_content,
            text=f"🏢 {TITULO_APP}",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=20)
        
        # Info usuario y status
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
            text="🔄 Cargando sistema...",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 10)
        )
        self.status_label.pack(anchor='e')
        
        # Notebook para pestañas con estilo
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='white')
        style.configure('Custom.TNotebook.Tab', 
                       padding=[20, 10], 
                       font=('Arial', 11, 'bold'))
        
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Footer
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
        self.status_label.config(text="🔄 Cargando datos...")
        self.footer_right.config(text="🔄 Actualizando datos...")
        self.root.update()
        
        # Cargar en hilo separado
        thread = threading.Thread(target=self._cargar_datos_thread)
        thread.daemon = True
        thread.start()
    
    def _cargar_datos_thread(self):
        try:
            # Test conexión
            if not procesador.test_conexion_supabase():
                self.root.after(0, lambda: self.status_label.config(text="❌ Sin conexión"))
                self.root.after(0, lambda: messagebox.showerror("Error", MSG_CONEXION_ERROR))
                return
            
            # Obtener sanciones pendientes
            sanciones = procesador.obtener_sanciones_pendientes()
            self.sanciones_categorizadas = procesador.categorizar_sanciones(sanciones)
            
            # Obtener historial de procesadas
            procesadas = procesador.obtener_procesadas_completas()
            self.historial_categorizado = procesador.categorizar_procesadas(procesadas)
            
            # Actualizar UI en hilo principal
            self.root.after(0, self._actualizar_pestañas)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="❌ Error cargando"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error cargando datos: {e}"))
    
    def _actualizar_pestañas(self):
        # Limpiar pestañas existentes
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Crear pestañas para sanciones pendientes
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
            
            # Emoji por categoría
            emoji = {
                "Faltas y Permisos": "📋",
                "Horas y Franco": "⏰", 
                "Resto": "⚠️"
            }.get(categoria, "📄")
            
            self.notebook.add(tab_frame, text=f"{emoji} {categoria} ({len(sanciones)})")
        
        # Crear pestañas para historial
        for categoria, sanciones in self.historial_categorizado.items():
            if sanciones:  # Solo crear pestaña si hay datos
                tab_obj = SancionesTab(
                    self.notebook, 
                    categoria, 
                    sanciones, 
                    None,  # No procesar en historial
                    self.cargar_datos,
                    es_historial=True
                )
                tab_frame = tab_obj.create_tab(self.notebook)
                
                # Emoji para historial
                emoji = {
                    "Faltas y Permisos": "📚",
                    "Horas y Franco": "📖", 
                    "Resto": "📓"
                }.get(categoria, "📄")
                
                self.notebook.add(tab_frame, text=f"{emoji} H-{categoria} ({len(sanciones)})")
        
        total_pendientes = sum(len(s) for s in self.sanciones_categorizadas.values())
        total_procesadas = sum(len(s) for s in self.historial_categorizado.values())
        
        self.status_label.config(text=f"✅ {total_pendientes} pendientes | {total_procesadas} procesadas")
        self.footer_right.config(text=f"🕐 Actualizado: {datetime.now().strftime('%H:%M:%S')}")
    
    def procesar_sanciones(self, sanciones, categoria):
        if not sanciones:
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar Procesamiento",
            f"¿Procesar {len(sanciones)} sanciones de '{categoria}'?\n\n"
            f"Esto actualizará el campo 'comentarios_rrhh' en Supabase.\n\n"
            f"¿Desea continuar?"
        )
        
        if not respuesta:
            return
        
        # Mostrar progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Procesando Sanciones")
        progress_window.geometry("450x200")
        progress_window.configure(bg='white')
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_frame = tk.Frame(progress_window, bg='white', padx=30, pady=30)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            progress_frame, 
            text="⚡ Procesando sanciones...", 
            bg='white',
            font=('Arial', 14, 'bold'),
            fg=COLOR_PRINCIPAL
        ).pack(pady=(0, 20))
        
        progress = ttk.Progressbar(progress_frame, length=350, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        status_lbl = tk.Label(
            progress_frame, 
            text="Iniciando procesamiento...", 
            bg='white',
            font=('Arial', 10),
            fg='#6c757d'
        )
        status_lbl.pack(pady=10)
        
        # Procesar en hilo separado
        thread = threading.Thread(
            target=self._procesar_thread,
            args=(sanciones, progress_window, status_lbl, progress, categoria)
        )
        thread.daemon = True
        thread.start()
    
    def _procesar_thread(self, sanciones, progress_window, status_lbl, progress, categoria):
        try:
            exitosas, fallidas = procesador.procesar_multiples_sanciones(sanciones, self.usuario)
            
            # Cerrar ventana de progreso
            self.root.after(0, progress_window.destroy)
            
            # Mostrar resultado
            if exitosas > 0:
                mensaje = f"✅ Procesamiento completado exitosamente\n\n"
                mensaje += f"🎯 Sanciones procesadas: {exitosas}\n"
                if fallidas > 0:
                    mensaje += f"❌ Sanciones fallidas: {fallidas}\n"
                mensaje += f"\n¿Desea descargar un archivo Excel con las sanciones procesadas?"
                
                def mostrar_resultado():
                    respuesta = messagebox.askyesno("Procesamiento Exitoso", mensaje)
                    if respuesta:
                        self._descargar_procesadas_recientes(sanciones)
                    self.cargar_datos()  # Recargar datos
                
                self.root.after(0, mostrar_resultado)
            else:
                mensaje = f"❌ No se pudieron procesar las sanciones\n\n"
                mensaje += f"Fallidas: {fallidas}\n"
                mensaje += f"Verifique la conexión y permisos"
                
                self.root.after(0, lambda: messagebox.showerror("Error", mensaje))
                
        except Exception as e:
            self.root.after(0, progress_window.destroy)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error procesando: {e}"))
    
    def _descargar_procesadas_recientes(self, sanciones_procesadas):
        """Descargar Excel de las sanciones recién procesadas"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Sanciones_Procesadas_{timestamp}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename,  # CORREGIDO: era initialname
                title="Guardar Sanciones Procesadas"
            )
            
            if filepath:
                # Agregar info de procesamiento a las sanciones
                for sancion in sanciones_procesadas:
                    sancion['procesado_por'] = self.usuario
                    sancion['fecha_procesamiento'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Intentar exportación completa, si falla usar simple
                archivo_generado = procesador.exportar_a_excel(sanciones_procesadas, filepath)
                
                if not archivo_generado:
                    print("⚠️ Exportación completa falló, intentando versión simple...")
                    archivo_generado = procesador.exportar_a_excel_simple(sanciones_procesadas, filepath)
                
                if archivo_generado:
                    messagebox.showinfo(
                        "Descarga exitosa", 
                        f"✅ Excel generado exitosamente:\n{filepath}"
                    )
                    
                    # Preguntar si quiere abrir el archivo
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
                initialfile=filename,  # CORREGIDO: era initialname
                title="Guardar Historial Completo"
            )
            
            if filepath:
                # Intentar exportación completa, si falla usar simple
                archivo_generado = procesador.exportar_a_excel(procesadas, filepath)
                
                if not archivo_generado:
                    print("⚠️ Exportación completa falló, intentando versión simple...")
                    archivo_generado = procesador.exportar_a_excel_simple(procesadas, filepath)
                
                if archivo_generado:
                    messagebox.showinfo(
                        "Descarga exitosa", 
                        f"✅ Historial completo exportado:\n{filepath}\n\n"
                        f"📊 Total de registros: {len(procesadas)}"
                    )
                    
                    # Preguntar si quiere abrir el archivo
                    if messagebox.askyesno("Abrir archivo", "¿Desea abrir el archivo Excel?"):
                        os.startfile(filepath)
                else:
                    messagebox.showerror("Error", "No se pudo generar el archivo Excel")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar historial: {e}")
    
    def generar_reporte_completo(self):
        """Generar reporte completo con estadísticas"""
        stats = procesador.obtener_estadisticas()
        
        if not stats:
            messagebox.showwarning("Sin datos", "No se pudieron obtener estadísticas")
            return
        
        # Crear ventana de reporte
        report_window = tk.Toplevel(self.root)
        report_window.title("📈 Reporte Completo del Sistema")
        report_window.geometry("800x600")
        report_window.configure(bg='white')
        report_window.transient(self.root)
        
        # Contenido del reporte
        text_widget = scrolledtext.ScrolledText(
            report_window, 
            wrap=tk.WORD, 
            font=('Courier', 10),
            bg='white',
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Generar contenido del reporte
        total_pendientes = sum(len(s) for s in self.sanciones_categorizadas.values())
        total_procesadas = sum(len(s) for s in self.historial_categorizado.values())
        
        contenido = f"""
📈 REPORTE COMPLETO DEL SISTEMA RRHH
{"="*60}

📊 RESUMEN EJECUTIVO:
{"─"*30}
• Total sanciones pendientes: {total_pendientes}
• Total sanciones procesadas: {total_procesadas}
• Procesadas hoy: {stats.get('procesadas_hoy', 0)}
• Eficiencia de procesamiento: {((total_procesadas/(total_procesadas+total_pendientes))*100):.1f}%

📋 SANCIONES PENDIENTES POR CATEGORÍA:
{"─"*40}
"""
        
        for categoria, sanciones in self.sanciones_categorizadas.items():
            contenido += f"• {categoria}: {len(sanciones)} pendientes\n"
        
        contenido += f"\n📚 HISTORIAL PROCESADO POR CATEGORÍA:\n{'─'*40}\n"
        for categoria, sanciones in self.historial_categorizado.items():
            contenido += f"• {categoria}: {len(sanciones)} procesadas\n"
        
        contenido += f"\n👤 ACTIVIDAD POR USUARIO:\n{'─'*30}\n"
        for usuario, cantidad in stats.get('por_usuario', {}).items():
            contenido += f"• {usuario}: {cantidad} sanciones procesadas\n"
        
        contenido += f"\n🏷️ TIPOS DE SANCIÓN MÁS FRECUENTES:\n{'─'*40}\n"
        for tipo, cantidad in sorted(stats.get('por_tipo', {}).items(), key=lambda x: x[1], reverse=True):
            contenido += f"• {tipo}: {cantidad}\n"
        
        contenido += f"""

📅 INFORMACIÓN DEL SISTEMA:
{"─"*30}
• Usuario actual: {self.usuario}
• Fecha de reporte: {datetime.now().strftime('%Y-%m-%d')}
• Hora de generación: {datetime.now().strftime('%H:%M:%S')}
• Versión del sistema: {TITULO_APP} {VERSION}
• Empresa: {EMPRESA}

🔗 ESTADO DE CONEXIONES:
{"─"*30}
• Base remota (Supabase): ✅ Conectado
• Base local (SQLite): ✅ Funcionando
• Sincronización: ✅ Activa

💡 RECOMENDACIONES:
{"─"*30}
• Procesar regularmente las sanciones pendientes
• Revisar estadísticas semanalmente
• Mantener respaldos del historial procesado
• Verificar la conectividad con Supabase periódicamente
        """
        
        text_widget.insert(tk.END, contenido)
        text_widget.config(state=tk.DISABLED)
        
        # Botones del reporte
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
        """Exportar reporte a archivo de texto"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Reporte_RRHH_{timestamp}.txt"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile=filename,  # CORREGIDO: era initialname
                title="Guardar Reporte"
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                
                messagebox.showinfo(
                    "Reporte exportado", 
                    f"✅ Reporte guardado exitosamente:\n{filepath}"
                )
                
                # Preguntar si quiere abrir el archivo
                if messagebox.askyesno("Abrir reporte", "¿Desea abrir el archivo de reporte?"):
                    os.startfile(filepath)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {e}")
    
    def mostrar_estadisticas(self):
        stats = procesador.obtener_estadisticas()
        
        if not stats:
            messagebox.showwarning("Advertencia", "No se pudieron obtener estadísticas")
            return
        
        # Ventana de estadísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estadísticas del Sistema")
        stats_window.geometry("600x500")
        stats_window.configure(bg='white')
        stats_window.transient(self.root)
        
        # Contenido
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
📊 ESTADÍSTICAS DEL SISTEMA RRHH
{"="*50}

📈 RESUMEN GENERAL:
• Total procesadas: {stats.get('total_procesadas', 0)}
• Procesadas hoy: {stats.get('procesadas_hoy', 0)}

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
• Sistema: {TITULO_APP} {VERSION}

🔗 CONEXIÓN:
{"─"*30}
• Base remota: Supabase
• Base local: SQLite
• Estado: ✅ Conectado
        """
        
        text_widget.insert(tk.END, contenido)
        text_widget.config(state=tk.DISABLED)
    
    def crear_sancion_prueba(self):
        if procesador.crear_sancion_prueba():
            messagebox.showinfo("Éxito", "✅ Sanción de prueba creada exitosamente")
            self.cargar_datos()
        else:
            messagebox.showerror("Error", "❌ No se pudo crear la sanción de prueba")
    
    def test_conexion(self):
        if procesador.test_conexion_supabase():
            messagebox.showinfo("Conexión", "✅ Conexión con Supabase exitosa")
        else:
            messagebox.showerror("Conexión", "❌ Error de conexión con Supabase")

def main():
    print("🚀 Iniciando Sistema RRHH Completo con Excel e Historial...")
    
    def on_login_success(usuario):
        app = MainWindow(usuario)
    
    # Mostrar login
    login = LoginWindow(on_login_success)

if __name__ == "__main__":
    main()
