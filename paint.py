import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog

# --- 1. Settings ---
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 500
DEFAULT_PEN_COLOR = "black"
DEFAULT_PEN_SIZE = 3
ERASER_SIZE = 15 # Eraser size

# --- 2. Main Paint Application Class ---
class PaintApp:
    def __init__(self, master):
        self.master = master
        master.title("Tkinter Paint Application") # Window title
        master.geometry(f"{CANVAS_WIDTH + 150}x{CANVAS_HEIGHT + 100}") # Main window dimensions, adjusted for side panel

        self.pen_color = DEFAULT_PEN_COLOR
        self.pen_size = DEFAULT_PEN_SIZE
        self.old_x = None
        self.old_y = None
        self.drawing_mode = "pen" # "pen", "eraser", "line", "rectangle", "circle", "text"
        self.start_x_shape = None # For shape drawing
        self.start_y_shape = None # For shape drawing
        self.current_shape_id = None # To dynamically update shape previews

        self._create_widgets() # Create UI elements
        self._bind_mouse_events() # Bind mouse events to canvas

    def _create_widgets(self):
        # --- Top Control Frame (Toolbar) ---
        self.control_frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # --- Tools Group ---
        self.tools_frame = tk.LabelFrame(self.control_frame, text="Tools", padx=5, pady=5)
        self.tools_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")

        self.pen_button = tk.Button(self.tools_frame, text="Pen", command=self.set_pen_mode, width=8)
        self.pen_button.pack(pady=2)
        self.eraser_button = tk.Button(self.tools_frame, text="Eraser", command=self.set_eraser_mode, width=8)
        self.eraser_button.pack(pady=2)
        self.clear_button = tk.Button(self.tools_frame, text="Clear All", command=self.clear_canvas, width=8)
        self.clear_button.pack(pady=2)
        self.text_button = tk.Button(self.tools_frame, text="Text", command=self.set_text_mode, width=8)
        self.text_button.pack(pady=2)


        # --- Shapes Group ---
        self.shapes_frame = tk.LabelFrame(self.control_frame, text="Shapes", padx=5, pady=5)
        self.shapes_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ns")

        self.line_button = tk.Button(self.shapes_frame, text="Line", command=self.set_line_mode, width=8)
        self.line_button.pack(pady=2)
        self.rect_button = tk.Button(self.shapes_frame, text="Rectangle", command=self.set_rectangle_mode, width=8)
        self.rect_button.pack(pady=2)
        self.circle_button = tk.Button(self.shapes_frame, text="Circle", command=self.set_circle_mode, width=8)
        self.circle_button.pack(pady=2)

        # --- Pen Size Group ---
        self.size_frame = tk.LabelFrame(self.control_frame, text="Size", padx=5, pady=5)
        self.size_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ns")

        self.size_small_button = tk.Button(self.size_frame, text="Small", command=lambda: self.set_pen_size(3), width=8)
        self.size_small_button.pack(pady=2)
        self.size_medium_button = tk.Button(self.size_frame, text="Medium", command=lambda: self.set_pen_size(8), width=8)
        self.size_medium_button.pack(pady=2)
        self.size_large_button = tk.Button(self.size_frame, text="Large", command=lambda: self.set_pen_size(15), width=8)
        self.size_large_button.pack(pady=2)

        # --- Colors Group ---
        self.colors_frame = tk.LabelFrame(self.control_frame, text="Colors", padx=5, pady=5)
        self.colors_frame.grid(row=0, column=3, padx=5, pady=5, sticky="ns")

        self.color_picker_button = tk.Button(self.colors_frame, text="More Colors...", command=self.choose_color, width=12)
        self.color_picker_button.pack(pady=2)

        # Quick color buttons
        self.quick_colors_frame = tk.Frame(self.colors_frame)
        self.quick_colors_frame.pack(pady=2)
        colors = ["black", "gray", "white", "red", "orange", "yellow", "green", "blue", "purple"]
        for i, color in enumerate(colors):
            btn = tk.Button(self.quick_colors_frame, bg=color, width=2, height=1, relief=tk.RIDGE,
                            command=lambda c=color: self.set_pen_color(c))
            btn.grid(row=i // 3, column=i % 3, padx=1, pady=1)

        # --- Drawing Canvas ---
        self.canvas = tk.Canvas(self.master, bg="white", width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bd=2, relief=tk.SUNKEN)
        self.canvas.pack(pady=10)

    def _bind_mouse_events(self):
        """Binds mouse events to the canvas based on the drawing mode."""
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_click(self, event):
        """Handles mouse clicks based on the current drawing mode."""
        if self.drawing_mode in ["pen", "eraser"]:
            self.old_x = event.x
            self.old_y = event.y
        elif self.drawing_mode in ["line", "rectangle", "circle"]:
            if self.start_x_shape is None: # First click for shape
                self.start_x_shape = event.x
                self.start_y_shape = event.y
            else: # Second click for shape
                self._draw_final_shape(event.x, event.y)
                self.start_x_shape = None # Reset for next shape
                self.start_y_shape = None
                self.current_shape_id = None # Clear preview
        elif self.drawing_mode == "text":
            self._draw_text(event.x, event.y)

    def on_mouse_drag(self, event):
        """Handles mouse drag events based on the current drawing mode."""
        if self.drawing_mode in ["pen", "eraser"]:
            self.draw_line(event)
        elif self.drawing_mode in ["line", "rectangle", "circle"]:
            if self.start_x_shape is not None:
                self._preview_shape(event.x, event.y)

    def on_mouse_release(self, event):
        """Handles mouse release events based on the current drawing mode."""
        if self.drawing_mode in ["pen", "eraser"]:
            self.old_x = None
            self.old_y = None
        # For shapes, the final drawing is done on the second click, not release

    def draw_line(self, event):
        """Draws a line while dragging the mouse (for pen/eraser modes)."""
        if self.old_x is not None and self.old_y is not None:
            current_color = "white" if self.drawing_mode == "eraser" else self.pen_color
            current_size = ERASER_SIZE if self.drawing_mode == "eraser" else self.pen_size
            
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                     width=current_size, fill=current_color,
                                     capstyle=tk.ROUND, smooth=tk.TRUE)
            self.old_x = event.x
            self.old_y = event.y

    def _preview_shape(self, current_x, current_y):
        """Draws a temporary preview of the shape while dragging."""
        if self.current_shape_id:
            self.canvas.delete(self.current_shape_id) # Delete previous preview

        fill_color = "" # Shapes are outlines by default
        
        if self.drawing_mode == "line":
            self.current_shape_id = self.canvas.create_line(self.start_x_shape, self.start_y_shape, current_x, current_y,
                                                            fill=self.pen_color, width=self.pen_size, dash=(4, 2))
        elif self.drawing_mode == "rectangle":
            self.current_shape_id = self.canvas.create_rectangle(self.start_x_shape, self.start_y_shape, current_x, current_y,
                                                                outline=self.pen_color, width=self.pen_size, dash=(4, 2))
        elif self.drawing_mode == "circle":
            # Calculate radius from start to current point
            radius = ((current_x - self.start_x_shape)**2 + (current_y - self.start_y_shape)**2)**0.5
            # Bounding box for oval (circle)
            x1 = self.start_x_shape - radius
            y1 = self.start_y_shape - radius
            x2 = self.start_x_shape + radius
            y2 = self.start_y_shape + radius
            self.current_shape_id = self.canvas.create_oval(x1, y1, x2, y2,
                                                            outline=self.pen_color, width=self.pen_size, dash=(4, 2))
        self.canvas.tag_raise(self.current_shape_id) # Ensure preview is on top

    def _draw_final_shape(self, end_x, end_y):
        """Draws the final shape after the second click."""
        if self.current_shape_id:
            self.canvas.delete(self.current_shape_id) # Delete preview
            self.current_shape_id = None

        if self.drawing_mode == "line":
            self.canvas.create_line(self.start_x_shape, self.start_y_shape, end_x, end_y,
                                    fill=self.pen_color, width=self.pen_size, capstyle=tk.ROUND)
        elif self.drawing_mode == "rectangle":
            self.canvas.create_rectangle(self.start_x_shape, self.start_y_shape, end_x, end_y,
                                        outline=self.pen_color, width=self.pen_size)
        elif self.drawing_mode == "circle":
            radius = ((end_x - self.start_x_shape)**2 + (end_y - self.start_y_shape)**2)**0.5
            x1 = self.start_x_shape - radius
            y1 = self.start_y_shape - radius
            x2 = self.start_x_shape + radius
            y2 = self.start_y_shape + radius
            self.canvas.create_oval(x1, y1, x2, y2, outline=self.pen_color, width=self.pen_size)

    def _draw_text(self, x, y):
        """Prompts for text input and draws it on the canvas."""
        text_input = simpledialog.askstring("Text Input", "Enter your text:")
        if text_input:
            self.canvas.create_text(x, y, text=text_input, fill=self.pen_color,
                                     font=("Arial", self.pen_size * 2, "normal"), anchor="nw")
        self.set_pen_mode() # Revert to pen mode after text input

    def clear_canvas(self):
        """Clears all contents from the canvas."""
        self.canvas.delete("all")

    def choose_color(self):
        """Opens the color selection palette."""
        color_code = colorchooser.askcolor(title="Choose Pen Color")
        if color_code[1]: # If a color was selected
            self.pen_color = color_code[1]
            self.set_pen_mode() # Revert to pen mode after choosing color

    def set_pen_color(self, color):
        """Sets the pen color directly from quick color buttons."""
        self.pen_color = color
        self.set_pen_mode() # Revert to pen mode

    def set_pen_size(self, size):
        """Sets the pen size."""
        self.pen_size = size
        self.set_pen_mode() # Revert to pen mode

    # --- Mode Setting Functions ---
    def set_pen_mode(self):
        self.drawing_mode = "pen"
        self.canvas.config(cursor="arrow") # Default cursor
        self.start_x_shape = None # Reset shape drawing state
        self.start_y_shape = None
        if self.current_shape_id: self.canvas.delete(self.current_shape_id)
        print("Mode: Pen")

    def set_eraser_mode(self):
        self.drawing_mode = "eraser"
        self.canvas.config(cursor="dot") # Eraser cursor
        self.start_x_shape = None
        self.start_y_shape = None
        if self.current_shape_id: self.canvas.delete(self.current_shape_id)
        print("Mode: Eraser")

    def set_line_mode(self):
        self.drawing_mode = "line"
        self.canvas.config(cursor="cross") # Crosshair cursor for shapes
        self.start_x_shape = None
        self.start_y_shape = None
        if self.current_shape_id: self.canvas.delete(self.current_shape_id)
        print("Mode: Line (Click twice: start and end points)")

    def set_rectangle_mode(self):
        self.drawing_mode = "rectangle"
        self.canvas.config(cursor="cross")
        self.start_x_shape = None
        self.start_y_shape = None
        if self.current_shape_id: self.canvas.delete(self.current_shape_id)
        print("Mode: Rectangle (Click twice: opposite corners)")

    def set_circle_mode(self):
        self.drawing_mode = "circle"
        self.canvas.config(cursor="cross")
        self.start_x_shape = None
        self.start_y_shape = None
        if self.current_shape_id: self.canvas.delete(self.current_shape_id)
        print("Mode: Circle (Click twice: center and a point on circumference)")

    def set_text_mode(self):
        self.drawing_mode = "text"
        self.canvas.config(cursor="xterm") # Text cursor
        self.start_x_shape = None
        self.start_y_shape = None
        if self.current_shape_id: self.canvas.delete(self.current_shape_id)
        print("Mode: Text (Click to place, then type in dialog)")


# --- 3. Run the application ---
if __name__ == "__main__":
    root = tk.Tk() # Create the main Tkinter window
    app = PaintApp(root) # Create an instance of the paint application
    root.mainloop() # Start the main Tkinter loop (keeps the application open)
    