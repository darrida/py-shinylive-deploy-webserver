from module import function_to_import
from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.page_sidebar(
        ui.sidebar(
            ui.markdown("v2024.06.29b")
        )
    ),
    ui.input_action_button("tests_btn", "Run tests app 1"),
    title="App1"
)


def server(input: Inputs, output: Outputs, session: Session):
    function_to_import()


app = App(app_ui, server)