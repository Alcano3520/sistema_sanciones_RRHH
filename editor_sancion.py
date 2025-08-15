# editor_sancion.py - Ventana para editar sanciones
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import *
from procesador import procesador

class EditorSancion:
    def __init__(self, parent, sancion, on_saved=None):
        self.parent = parent
        self.sancion = sancion.copy()
        self.on_saved = on_saved
        self.ventana = None
        self.campos = {}
        
        self.crear_ventana()
    
    def crear_ventana(self):
        """Crear ventana de edición"""
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title(f"Editar Sanción - {self.sancion.get('empleado_nombre', 'N/A')}")
        self.ventana.geometry("600x700")
        self.ventana.resizable(True, True)
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Frame principal con scroll
        main_frame = tk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=COLOR_PRINCIPAL)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header_frame,
            text=f"📝 Editar Sanción",
            bg=COLOR_PRINCIPAL,
            fg='white',
            font=('Arial', 14, 'bold'),
            pady=10
        ).pack()
        
        # Frame de campos con scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Crear campos editables
        self.crear_campos(scrollable_frame)
        
        # Frame de botones
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Botones
        tk.Button(
            btn_frame,
            text="💾 Guardar Cambios",
            command=self.guardar_cambios,
            bg=COLOR_EXITO,
            fg='white',
            font=('Arial', 11, 'bold'),
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="🔄 Procesar para Nómina",
            command=self.procesar_nomina,
            bg=COLOR_SECUNDARIO,
            fg='white',
            font=('Arial', 11, 'bold'),
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=self.ventana.destroy,
            bg='gray',
            fg='white',
            font=('Arial', 11),
            pady=8
        ).pack(side=tk.RIGHT)
        
        # Focus en primer campo
        if self.campos:
            next(iter(self.campos.values())).focus()
    
    def crear_campos(self, parent):
        """Crear campos editables"""
        
        # Campos principales
        campos_config = [
            ('empleado_cod', 'Código Empleado', 'number'),
            ('empleado_nombre', 'Nombre Empleado', 'text'),
            ('puesto', 'Puesto', 'text'),
            ('agente', 'Agente', 'text'),
            ('fecha', 'Fecha', 'date'),
            ('hora', 'Hora', 'time'),
            ('tipo_sancion', 'Tipo Sanción', 'combo'),
            ('observaciones', 'Observaciones', 'textarea'),
            ('observaciones_adicionales', 'Observaciones Adicionales', 'textarea'),
            ('comentarios_gerencia', 'Comentarios Gerencia', 'textarea'),
            ('comentarios_rrhh', 'Comentarios RRHH', 'textarea'),
            ('horas_extras', 'Horas Extras', 'number')
        ]
        
        row = 0
        for campo, etiqueta, tipo in campos_config:
            # Etiqueta
            tk.Label(
                parent,
                text=f"{etiqueta}:",
                font=('Arial', 10, 'bold'),
                anchor='w'
            ).grid(row=row, column=0, sticky='w', padx=(0, 10), pady=(10, 5))
            
            # Campo según tipo
            if tipo == 'text':
                widget = tk.Entry(parent, font=('Arial', 10), width=50)
                widget.insert(0, str(self.sancion.get(campo, '')))
                
            elif tipo == 'number':
                widget = tk.Entry(parent, font=('Arial', 10), width=20)
                valor = self.sancion.get(campo, '')
                if valor is not None:
                    widget.insert(0, str(valor))
                    
            elif tipo == 'date':
                widget = tk.Entry(parent, font=('Arial', 10), width=20)
                valor = self.sancion.get(campo, '')
                if valor:
                    # Convertir fecha si es necesario
                    if isinstance(valor, str):
                        widget.insert(0, valor.split('T')[0])  # Solo fecha, sin hora
                    else:
                        widget.insert(0, str(valor))
                        
            elif tipo == 'time':
                widget = tk.Entry(parent, font=('Arial', 10), width=20)
                valor = self.sancion.get(campo, '')
                if valor:
                    widget.insert(0, str(valor))
                    
            elif tipo == 'combo':
                widget = ttk.Combobox(parent, font=('Arial', 10), width=47)
                # Opciones de tipos de sanción
                tipos_sancion = []
                for categoria, tipos in CATEGORIAS.items():
                    tipos_sancion.extend(tipos)
                widget['values'] = tipos_sancion
                widget.set(self.sancion.get(campo, ''))
                
            elif tipo == 'textarea':
                widget = tk.Text(parent, font=('Arial', 10), width=50, height=3)
                valor = self.sancion.get(campo, '')
                if valor:
                    widget.insert('1.0', str(valor))
            
            widget.grid(row=row, column=1, sticky='ew', padx=(0, 10), pady=(5, 10))
            
            # Configurar expansión
            parent.grid_columnconfigure(1, weight=1)
            
            # Guardar referencia
            self.campos[campo] = widget
            row += 1
        
        # Información adicional
        info_frame = tk.LabelFrame(parent, text="Información del Sistema", font=('Arial', 10, 'bold'))
        info_frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=(0, 10), pady=20, ipadx=10, ipady=10)
        
        info_text = f"""
ID: {self.sancion.get('id', 'N/A')}
Status: {self.sancion.get('status', 'N/A')}
Creado: {self.sancion.get('created_at', 'N/A')}
Actualizado: {self.sancion.get('updated_at', 'N/A')}
        """.strip()
        
        tk.Label(
            info_frame,
            text=info_text,
            font=('Arial', 9),
            fg='gray',
            justify=tk.LEFT
        ).pack(anchor='w')
    
    def obtener_valores(self):
        """Obtener valores actuales de los campos"""
        valores = {}
        
        for campo, widget in self.campos.items():
            try:
                if isinstance(widget, tk.Text):
                    valor = widget.get('1.0', tk.END).strip()
                else:
                    valor = widget.get().strip()
                
                # Conversiones especiales
                if campo in ['empleado_cod', 'horas_extras'] and valor:
                    try:
                        valor = int(valor)
                    except ValueError:
                        valor = None
                elif not valor:
                    valor = None
                
                valores[campo] = valor
                
            except Exception as e:
                print(f"Error obteniendo valor de {campo}: {e}")
                valores[campo] = None
        
        return valores
    
    def validar_datos(self, datos):
        """Validar datos antes de guardar"""
        errores = []
        
        # Campos requeridos
        requeridos = ['empleado_cod', 'empleado_nombre', 'puesto', 'agente', 'fecha', 'hora', 'tipo_sancion']
        
        for campo in requeridos:
            if not datos.get(campo):
                etiqueta = campo.replace('_', ' ').title()
                errores.append(f"• {etiqueta} es requerido")
        
        # Validar código empleado
        if datos.get('empleado_cod'):
            try:
                codigo = int(datos['empleado_cod'])
                if codigo <= 0:
                    errores.append("• Código de empleado debe ser positivo")
            except (ValueError, TypeError):
                errores.append("• Código de empleado debe ser un número")
        
        # Validar tipo de sanción
        if datos.get('tipo_sancion'):
            tipos_validos = []
            for tipos in CATEGORIAS.values():
                tipos_validos.extend(tipos)
            if datos['tipo_sancion'] not in tipos_validos:
                errores.append(f"• Tipo de sanción no válido: {datos['tipo_sancion']}")
        
        return errores
    
    def guardar_cambios(self):
        """Guardar cambios en la sanción"""
        try:
            datos = self.obtener_valores()
            
            # Validar
            errores = self.validar_datos(datos)
            if errores:
                messagebox.showerror(
                    "Errores de Validación",
                    "No se pueden guardar los cambios:\n\n" + "\n".join(errores)
                )
                return
            
            # Confirmar cambios
            if not messagebox.askyesno(
                "Confirmar Cambios",
                f"¿Guardar los cambios en la sanción de {datos.get('empleado_nombre', 'N/A')}?"
            ):
                return
            
            # Actualizar en Supabase
            sancion_id = self.sancion['id']
            if procesador.actualizar_sancion_completa(sancion_id, datos):
                messagebox.showinfo("Éxito", "Sanción actualizada correctamente")
                
                # Actualizar sanción local
                self.sancion.update(datos)
                
                # Callback si existe
                if self.on_saved:
                    self.on_saved(self.sancion)
                
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la sanción")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando cambios: {e}")
    
    def procesar_nomina(self):
        """Procesar sanción para nómina (agregar comentario RRHH)"""
        try:
            if self.sancion.get('comentarios_rrhh'):
                if not messagebox.askyesno(
                    "Sanción ya Procesada",
                    "Esta sanción ya tiene comentarios de RRHH.\n¿Desea procesarla de nuevo?"
                ):
                    return
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            usuario = "RRHH"  # Podría obtenerse del login
            comentario = f"{MSG_PROCESADO} - {fecha_actual} - {usuario}"
            
            # Actualizar solo comentario RRHH
            datos_update = {'comentarios_rrhh': comentario}
            
            sancion_id = self.sancion['id']
            if procesador.actualizar_sancion_completa(sancion_id, datos_update):
                messagebox.showinfo("Éxito", "Sanción procesada para nómina")
                
                # Actualizar campo local
                self.sancion['comentarios_rrhh'] = comentario
                
                # Actualizar widget
                if 'comentarios_rrhh' in self.campos:
                    widget = self.campos['comentarios_rrhh']
                    if isinstance(widget, tk.Text):
                        widget.delete('1.0', tk.END)
                        widget.insert('1.0', comentario)
                    else:
                        widget.delete(0, tk.END)
                        widget.insert(0, comentario)
                
                # Callback si existe
                if self.on_saved:
                    self.on_saved(self.sancion)
                    
            else:
                messagebox.showerror("Error", "No se pudo procesar la sanción")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando sanción: {e}")
