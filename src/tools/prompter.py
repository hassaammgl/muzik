from rich.console import Console

console = Console()


class Prompter:
    def clear(self):
        console.clear()

    def prompt(self, heading="", instructions="", options=None, user_choice=""):
        if options is None:
            options = []

        console.print(f"[bold green]{heading}")
        for index, data in enumerate(options, start=1):
            choice = data["value"]
            if user_choice == choice:
                console.print(
                    f"[bold green1]{index})[/bold green1] [wheat1]{data['prompt']} [default]"
                )
            else:
                console.print(f"{index}) {data['prompt']}")
        options_nums = "|".join(str(i) for i in range(1, len(options) + 1))
        console.print(
            f"[bold italic yellow]{instructions} {options_nums} and 0 to exit"
        )
        while True:
            user_input = int(input("Enter choice number: "))
            if user_input == 0:
                exit(0)
            elif user_input.is_integer() and 1 <= int(user_input) <= len(options):
                return options[user_input - 1]
            else:
                console.print("[bold red]Invalid choice! Try Again.[/bold red]")
