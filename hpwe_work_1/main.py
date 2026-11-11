from lighting.app import LightingApp


def main() -> None:
    """Создаёт окно и запускает обработку действий пользователя."""
    app = LightingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
