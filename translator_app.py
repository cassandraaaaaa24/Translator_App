import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
import easyocr
from deep_translator import GoogleTranslator
from PIL import Image, ImageTk
import os

# Initialize OCR reader and translator
reader = easyocr.Reader(['en'])  # You can add more languages like ['en', 'fr', 'de']

def select_image():
    """Open file dialog to select an image."""
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
    )
    if file_path:
        image_path_var.set(file_path)
        display_image(file_path)

def clear_image():
    """Clear selected image path and preview."""
    image_path_var.set("")
    image_label.config(image="")
    image_label.image = None
    image_label.config(text="No image selected")

def display_image(path):
    """Display selected image in the UI."""
    try:
        img = Image.open(path)
        img.thumbnail((300, 300))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk, text="")
        image_label.image = img_tk
    except Exception as e:
        messagebox.showerror("Error", f"Unable to load image: {e}")

def process_image():
    """Translate typed text, or OCR image text when typed text is empty."""
    path = image_path_var.get()
    typed_text = input_text_var.get().strip()
    target_lang = language_map.get(lang_var.get().strip(), "")

    if not target_lang:
        messagebox.showwarning("Warning", "Please select a target language from the dropdown.")
        return

    try:
        if typed_text:
            extracted_text = typed_text
        else:
            if not os.path.exists(path):
                messagebox.showwarning("Warning", "Type text to translate or select a valid image.")
                return

            # OCR
            result = reader.readtext(path, detail=0)
            extracted_text = "\n".join(result)

        if not extracted_text.strip():
            messagebox.showinfo("Info", "No text detected in the image.")
            return

        # Translation
        translated_text = translate_text(extracted_text, target_lang)
        if not translated_text:
            return

        # Display results
        ocr_text_box.delete(1.0, tk.END)
        ocr_text_box.insert(tk.END, extracted_text)

        translated_text_box.delete(1.0, tk.END)
        translated_text_box.insert(tk.END, translated_text)

    except Exception as e:
        messagebox.showerror("Error", f"Processing failed: {e}")

def translate_text(text, target_lang):
    """Translate text to the target language."""
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        messagebox.showerror("Error", f"Translation failed: {e}")
        return ""

# --- UI Setup ---
root = tk.Tk()
root.title("Image Translator with EasyOCR")
root.geometry("980x760")
root.minsize(900, 680)

image_path_var = tk.StringVar()
lang_var = tk.StringVar()
input_text_var = tk.StringVar()
text_size_var = tk.IntVar(value=11)

supported_languages = GoogleTranslator().get_supported_languages(as_dict=True)
language_map = {}
for name, code in sorted(supported_languages.items(), key=lambda item: item[0].lower()):
    label = f"{name.title()} ({code})"
    language_map[label] = code

default_lang_label = next((label for label, code in language_map.items() if code == "es"), "")
lang_var.set(default_lang_label)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=12, pady=12)

combo_style = ttk.Style(root)

def apply_text_size(*_):
    """Apply selected text size to UI widgets for readability."""
    size = max(8, min(28, text_size_var.get()))
    text_size_var.set(size)
    ui_font = ("Segoe UI", size)

    combo_style.configure("Readable.TCombobox", font=ui_font)

    widgets = [
        select_button,
        clear_button,
        image_path_entry,
        text_size_label,
        text_size_spinbox,
        text_label,
        text_entry,
        lang_label,
        translate_button,
        extracted_label,
        translated_label,
        image_label,
        ocr_text_box,
        translated_text_box,
    ]

    for widget in widgets:
        try:
            widget.configure(font=ui_font)
        except tk.TclError:
            pass

def increase_text_size():
    """Increase text size by one point."""
    text_size_var.set(text_size_var.get() + 1)
    apply_text_size()

def decrease_text_size():
    """Decrease text size by one point."""
    text_size_var.set(text_size_var.get() - 1)
    apply_text_size()

# Image selection section (top)
image_section = tk.Frame(main_frame)
image_section.pack(fill="x", pady=(0, 10))

button_frame = tk.Frame(image_section)
button_frame.pack(side="left", anchor="n")

select_button = tk.Button(button_frame, text="Select Image", width=14, command=select_image)
select_button.pack(pady=(0, 8))
clear_button = tk.Button(button_frame, text="Clear Image", width=14, command=clear_image)
clear_button.pack()

preview_frame = tk.Frame(image_section, bd=1, relief="solid")
preview_frame.pack(side="left", fill="both", expand=True, padx=(12, 0))

image_label = tk.Label(
    preview_frame,
    text="No image selected",
    width=52,
    height=14,
    anchor="center"
)
image_label.pack(fill="both", expand=True)

image_path_entry = tk.Entry(main_frame, textvariable=image_path_var, width=100)
image_path_entry.pack(fill="x", pady=(0, 12))

text_size_frame = tk.Frame(main_frame)
text_size_frame.pack(anchor="w", pady=(0, 10))

text_size_label = tk.Label(text_size_frame, text="Text Size:")
text_size_label.pack(side="left")

tk.Button(text_size_frame, text="-", width=3, command=decrease_text_size).pack(side="left", padx=(8, 4))

text_size_spinbox = tk.Spinbox(
    text_size_frame,
    from_=8,
    to=28,
    width=5,
    textvariable=text_size_var,
    command=apply_text_size
)
text_size_spinbox.pack(side="left")
text_size_spinbox.bind("<Return>", apply_text_size)
text_size_spinbox.bind("<FocusOut>", apply_text_size)

tk.Button(text_size_frame, text="+", width=3, command=increase_text_size).pack(side="left", padx=(4, 0))

# Text input and target language section (middle)
text_label = tk.Label(main_frame, text="Text to Translate:")
text_label.pack(anchor="w")
text_entry = tk.Entry(main_frame, textvariable=input_text_var, width=100)
text_entry.pack(fill="x", pady=(2, 10))

lang_label = tk.Label(main_frame, text="Target Language:")
lang_label.pack(anchor="w")
lang_combobox = ttk.Combobox(
    main_frame,
    textvariable=lang_var,
    values=list(language_map.keys()),
    state="readonly",
    style="Readable.TCombobox",
    width=38
)
lang_combobox.pack(anchor="w", pady=(2, 10))

translate_button = tk.Button(main_frame, text="Translate", command=process_image)
translate_button.pack(pady=(0, 12))

# Results section (bottom)
extracted_label = tk.Label(main_frame, text="Extracted Text:")
extracted_label.pack(anchor="w")
ocr_text_box = scrolledtext.ScrolledText(main_frame, height=7, width=100)
ocr_text_box.pack(fill="both", expand=True, pady=(2, 10))

translated_label = tk.Label(main_frame, text="Translated Text:")
translated_label.pack(anchor="w")
translated_text_box = scrolledtext.ScrolledText(main_frame, height=7, width=100)
translated_text_box.pack(fill="both", expand=True)

apply_text_size()

root.mainloop()
