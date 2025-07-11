from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from plyer import filechooser
from PIL import Image
import piexif
import os
import pandas as pd

class MetadataCleaner(BoxLayout):
    def __init__(self, **kwargs):
        super(MetadataCleaner, self).__init__(orientation='vertical', **kwargs)

        self.status = Label(text="Selecione uma imagem (.jpg) para remover os metadados.")
        self.add_widget(self.status)

        self.select_button = Button(text="Selecionar Imagem")
        self.select_button.bind(on_press=self.select_file)
        self.add_widget(self.select_button)

        self.output_input = TextInput(hint_text="Caminho para salvar imagem limpa", multiline=False)
        self.add_widget(self.output_input)

        self.report_input = TextInput(hint_text="Nome do relatório (ex: relatorio.txt)", multiline=False)
        self.add_widget(self.report_input)

        self.clean_button = Button(text="Remover Metadados e Gerar Relatório")
        self.clean_button.bind(on_press=self.clean_metadata)
        self.add_widget(self.clean_button)

        self.image_path = None

    def select_file(self, instance):
        filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        if selection:
            self.image_path = selection[0]
            self.status.text = f"Arquivo selecionado: {self.image_path}"
        else:
            self.status.text = "Nenhum arquivo selecionado."

    def clean_metadata(self, instance):
        if not self.image_path:
            self.status.text = "Nenhum arquivo selecionado."
            return

        output_path = self.output_input.text.strip()
        report_name = self.report_input.text.strip() or "relatorio.txt"
        output_path = output_path if output_path else self.image_path.replace(".jpg", "_limpo.jpg")

        try:
            # Abre imagem e salva sem os metadados
            img = Image.open(self.image_path)
            original_exif = piexif.load(img.info.get("exif", b""))

            img.save(output_path, "jpeg", exif=piexif.dump({}))

            # Coleta metadados originais para o relatório
            metadata = {
                "Arquivo Original": [self.image_path],
                "Arquivo Limpo": [output_path],
                "Resolução": [f"{img.width}x{img.height}"],
                "Tamanho (Bytes)": [os.path.getsize(self.image_path)]
            }

            df = pd.DataFrame(metadata)
            df.to_csv(report_name, index=False, sep="\t")

            self.status.text = f"Metadados removidos. Relatório salvo em {report_name}"

        except Exception as e:
            self.status.text = f"Erro: {str(e)}"

class MetadataCleanerApp(App):
    def build(self):
        return MetadataCleaner()

if __name__ == '__main__':
    MetadataCleanerApp().run()
