# import test_pyfetch as tests
from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.page_sidebar(
        ui.sidebar(
            ui.markdown("v2024.06.29b")
        )
    ),
    ui.input_action_button("tests_btn", "Run tests app 2"),
    title="App2"
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)