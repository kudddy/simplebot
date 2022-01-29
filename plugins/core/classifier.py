class Model:
    def __init__(self):
        self.data = {}

    def fit(self, train: dict):
        self.data.update(train)

    def predict(self, text: str):
        # TODO проработать вопрос с замыканием
        # пока возвращаем стейт с поиском
        return self.data.get(text, 1)
