"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config
from rembg import remove
from PIL import Image
from os.path import join, splitext
from os import unlink
# from reflex_motion import motion
import reflex as rx

filename = f"{config.app_name}/{config.app_name}.py"

class State(rx.State):
    img: list[str]

    async def handle_upload(self, files: list[rx.UploadFile]):
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.filename

            with outfile.open("wb") as file_object:
                file_object.write(upload_data)

            self.img.append(file.filename) 
            
    def clean_list(self, name):
        if name is True:
            self.img.clear()
        else:
            self.img.remove(name)
            unlink(join(rx.get_upload_dir(), name))
            
        
        
    def remove_bg(self, name):
        
        if name is True:
            for img in self.img:
                indice = self.img.index(img)
                self.img.remove(img)
                self.img.insert(indice, self.remove(img))
        else:
            indice = self.img.index(name)
            self.img.remove(name)
            self.img.insert(indice, self.remove(name))
            
        
        
    def remove(self, img):
        inp = Image.open(join(rx.get_upload_dir(), img))
        new_name = join(rx.get_upload_dir(), splitext(img)[0] + "_rmbg.png") 
        outp = remove(inp)
        outp.save(new_name)
        return splitext(img)[0] + "_rmbg.png"
        
                

color = "rgb(107,99,246)"


def index():
    return rx.center(
        rx.vstack(
        rx.upload(
            rx.vstack(
                rx.button("Select File", color=color, bg="white", border=f"1px solid {color}"),
                rx.text("Drag and drop files here or click to select files"),
            ),
            id="upload1",
            border=f"1px dotted {color}",
            padding="5em",
            on_drop=State.handle_upload(rx.upload_files(upload_id="upload1"))
        ),
        
        rx.flex(
            rx.button("Clear all", on_click=State.clean_list(True)),  
            rx.button("Remove Background", on_click=State.remove_bg(True)),
            spacing='2'
        ),
        
        rx.foreach(
            State.img,
            lambda img: rx.card(
                rx.inset(
                    rx.image(src=rx.get_upload_url(img), width="100%", height="auto"),
                    side="top",
                    pb="current",
                ),
                rx.flex(
                    rx.button(rx.icon(tag="circle-x"), "Eliminar",color_scheme="red", on_click=State.clean_list(img)),
                    rx.button(rx.icon(tag="eraser"), "Borrar fondo",color_scheme="blue", on_click=State.remove_bg(img)),
                    rx.button(rx.icon(tag="download"), "Descargar",color_scheme="green", on_click=rx.download(rx.get_upload_url(img))),
                    spacing="2",
                    direction="column"
                ),
                width="25vw",
            )
        ),
        padding="5em",
    )
)


app = rx.App(
    theme = rx.theme(appearance="dark", accentColor="plum", radius="large")
)
app.add_page(index)
