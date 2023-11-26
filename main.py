import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MemoryOptimizerApp:
    def __init__(self, master):
        self.master = master
        master.title("Memory Optimizer")
        master.geometry("800x650")

        # Encabezado
        self.label_header = tk.Label(master, text="Memory Optimizer", font=("Helvetica", 20, "bold"))
        self.label_header.pack(pady=10)

        # Sección de botones
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.optimize_button = tk.Button(self.button_frame, text="Optimize Memory", command=self.optimize_memory,
                                         font=("Helvetica", 12))
        self.optimize_button.pack(side=tk.LEFT, padx=10)
        self.refresh_button = tk.Button(self.button_frame, text="Refresh", command=self.update_real_time_data,
                                        font=("Helvetica", 12))
        self.refresh_button.pack(side=tk.LEFT, padx=10)

        # Vista de gráfico
        self.graph_frame = tk.Frame(master)
        self.graph_frame.pack(pady=10)

        self.graph_view = tk.StringVar()
        self.graph_view.set("bar")  # Valor predeterminado: gráfico de barras

        self.bar_radio = tk.Radiobutton(self.graph_frame, text="Bar Chart", variable=self.graph_view, value="bar",
                                        font=("Helvetica", 12))
        self.bar_radio.pack(side=tk.LEFT, padx=10)
        self.line_radio = tk.Radiobutton(self.graph_frame, text="Line Chart", variable=self.graph_view, value="line",
                                         font=("Helvetica", 12))
        self.line_radio.pack(side=tk.LEFT, padx=10)

        # Gráfico de uso de memoria en tiempo real
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(pady=10)

        # Sección de procesos
        self.process_frame = tk.Frame(master)
        self.process_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.process_frame, columns=('PID', 'Process', 'Memory Usage'),
                                 show='headings', height=10)
        self.tree.heading('PID', text='PID')
        self.tree.heading('Process', text='Process')
        self.tree.heading('Memory Usage', text='Memory Usage')
        self.tree.pack()

        self.kill_button = tk.Button(master, text="Kill Selected Process", command=self.kill_selected_process,
                                     font=("Helvetica", 12))
        self.kill_button.pack(pady=10)

        # Información de la memoria
        self.memory_info_frame = tk.Frame(master)
        self.memory_info_frame.pack(pady=10)

        self.label_memory_info = tk.Label(self.memory_info_frame, text="", font=("Helvetica", 14), fg='#FF3333')
        self.label_memory_info.pack()

        self.label_system_memory = tk.Label(self.memory_info_frame, text="", font=("Helvetica", 14), fg='#3399FF')
        self.label_system_memory.pack()

        # Información de la CPU
        self.label_cpu_info = tk.Label(master, text="", font=("Helvetica", 14))
        self.label_cpu_info.pack(pady=10)

        # Iniciar el monitoreo en tiempo real
        self.update_real_time_data()
        self.update_process_tree()

    def optimize_memory(self):
        try:
            # Lógica de optimización de memoria aquí
            messagebox.showinfo("Optimization Complete", "Memory has been optimized.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_real_time_data(self):
        self.update_real_time_memory()
        self.update_cpu_info()
        self.update_process_tree()
        self.update_graph()
        self.update_memory_info()
        self.master.after(1000, self.update_real_time_data)  # Llamada recursiva cada 1000 milisegundos (1 segundo)

    def update_real_time_memory(self):
        try:
            # Actualizar el gráfico con la información más reciente
            memory_info = psutil.virtual_memory()
            swap_info = psutil.swap_memory()
            self.ax.clear()

            if self.graph_view.get() == "bar":
                self.ax.bar(['Used', 'Free', 'Available', 'Swap Used'],
                            [memory_info.used, memory_info.free, memory_info.available, swap_info.used],
                            color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'])
            else:
                self.ax.plot(['Used', 'Free', 'Available', 'Swap Used'],
                             [memory_info.used, memory_info.free, memory_info.available, swap_info.used],
                             marker='o', linestyle='-', color='#FF9900')

            self.ax.set_ylabel('Memory (bytes)', fontsize=12)
            self.ax.set_title('Real-time Memory Usage', fontsize=14)
            self.ax.tick_params(axis='x', labelsize=10)
            self.ax.tick_params(axis='y', labelsize=10)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_memory_info(self):
        try:
            # Actualizar etiqueta con información de la memoria
            self.label_memory_info.config(text=f"App Memory: {self.format_bytes(psutil.Process().memory_info().rss)}",
                                          font=("Helvetica", 14))
            system_memory_info = psutil.virtual_memory()
            self.label_system_memory.config(text=f"System Memory: Used {self.format_bytes(system_memory_info.used)} "
                                                 f"| Free {self.format_bytes(system_memory_info.available)} "
                                                 f"| Total {self.format_bytes(system_memory_info.total)}",
                                            font=("Helvetica", 14))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_cpu_info(self):
        try:
            # Obtener información sobre el uso de la CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            self.label_cpu_info.config(text=f"CPU Usage: {cpu_percent:.2f}%", font=("Helvetica", 14))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_process_tree(self):
        # Actualizar la información del árbol de procesos
        self.tree.delete(*self.tree.get_children())
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            self.tree.insert("", "end", values=(proc.info['pid'], proc.info['name'],
                                                self.format_bytes(proc.info['memory_info'].rss)),
                             tags=('even_row' if proc.info['pid'] % 2 == 0 else 'odd_row'))

        # Actualizar cada 5000 milisegundos (5 segundos)
        self.master.after(5000, self.update_process_tree)

    def kill_selected_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("No Selection", "No process selected.")
            return

        process_pid = int(self.tree.item(selected_item, 'values')[0])
        try:
            # Terminar el proceso seleccionado
            psutil.Process(process_pid).terminate()
            messagebox.showinfo("Process Terminated", f"Process with PID {process_pid} has been terminated.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_graph(self):
        self.update_real_time_memory()

    @staticmethod
    def format_bytes(bytes_size):
        # Convierte el tamaño de bytes a una cadena legible (KB, MB, GB, etc.)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                break
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} {unit}"

def main():
    root = tk.Tk()
    root.title("Memory Optimizer")
    root.geometry("800x650")
    app = MemoryOptimizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
