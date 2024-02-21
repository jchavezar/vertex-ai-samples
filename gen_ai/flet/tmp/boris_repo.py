from operator import itemgetter

import flet as ft

from langchain_core.runnables import RunnableLambda, RunnablePassthrough


class UserEntry(ft.Row):
    def __init__(self, initials, send_message):

        super().__init__()

        self.send_message = send_message
        self.initials = initials
        self.vertical_alignment="start"

        self.controls = [
            # Avatar for Self
            ft.CircleAvatar(
                content=ft.Text(self.initials),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLACK,
            ),
            # A new message entry form
            ft.TextField(
                hint_text="Write a message...",
                autofocus=True,
                min_lines=1,
                max_lines=5,
                filled=True,
                expand=True,
                # Enter = send message, CTRL-Enter = new line
                shift_enter=True,                
                on_submit=self.send_message_click,
            ),
            # Send button for mouse users
            ft.IconButton(
                icon=ft.icons.SEND_ROUNDED,
                tooltip="Send message",
                on_click=self.send_message_click,
            )
        ]

    @property
    def value(self):
        return self.controls[1].value

    async def clear(self):
        self.controls[1].value = ''
        await self.update_async()

    async def send_message_click(self, e):
        await self.send_message(e)

class ChatMessage(ft.Row):
    def __init__(self, initials, message):

        super().__init__()

        self.initials = initials
        self.vertical_alignment="start"

        self.controls = [
            # Avatar for Self
            ft.CircleAvatar(
                content=ft.Text(self.initials),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLACK,
            ),
            ft.Text(message),
        ]


class FletChain(ft.UserControl):

    def __init__(self, chain, memory = None):

        super().__init__()

        self.chain = chain
        self.memory = memory
        self.user_entry = UserEntry('B', self.send_message_click)

        self.messages = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )

    async def send_message_click(self, e):

        inputs = {'input': self.user_entry.value}
        response = self.chain.invoke(inputs)
        if self.memory:
            self.memory.save_context(inputs, {"output": response.content})

        self.messages.controls.append(ChatMessage('B', self.user_entry.value))
        await self.user_entry.clear()
        self.messages.controls.append(ChatMessage('P', response.content))
        await self.update_async()

    def build(self):

        return ft.Column(
            controls=[
                ft.Container(content=self.messages),
                ft.Container(content=self.user_entry)
            ],
        )

async def main(page: ft.Page):

    model = ChatVertexAI()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful chatbot"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    memory = ConversationBufferMemory(return_messages=True)
    chain = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | model
    )


    appbar_items = [
        ft.PopupMenuItem(text="Login"),
        ft.PopupMenuItem(),  # divider
        ft.PopupMenuItem(text="Settings")
    ]
    appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.GRID_GOLDENRATIO_ROUNDED),
        leading_width=40,
        title=ft.Text("FletChain", text_align="start"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.Container(
                content=ft.PopupMenuButton(
                    items=appbar_items
                ),
                margin=ft.margin.only(left=50, right=25)
            )
        ],
    )
    page.appbar = appbar
    page.vertical_alignment = ft.MainAxisAlignment.END


    await page.add_async(FletChain(chain, memory))