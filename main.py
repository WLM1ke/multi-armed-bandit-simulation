import random

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import beta


def fill_data(duration: int, data: list[tuple[int, int]]) -> list[int]:
    out: list[int] = []
    value = 0
    pointer = 0
    data.sort()

    for i in range(duration):
        if pointer < len(data) and i == data[pointer][0]:
            value = data[pointer][1]
            pointer += 1

        out.append(value)

    return out


class Terminal:
    def __init__(
        self,
        duration: int,
        p_changes: list[tuple[float, float]],
    ) -> None:
        self.p = fill_data(duration, p_changes)
        self.count_success = [0] * duration
        self.count_fail = [0] * duration

    def beta(self, interval: int, window: int) -> float:
        end = interval + 1
        start = max(0, end - window)
        a = sum(self.count_success[start:end]) + 1
        b = sum(self.count_fail[start:end]) + 1

        return beta.rvs(a=a, b=b, size=1)[0]

    def sample(self, interval: int) -> None:
        match bool(random.random() < self.p[interval]):
            case True:
                self.count_success[interval] += 1
            case False:
                self.count_fail[interval] += 1


def main(
    duration: int,
    window: int,
    rps_changes: list[tuple[int, int]],
    p_a_changes: list[tuple[float, float]],
    p_b_changes: list[tuple[float, float]],
) -> None:
    t = list(range(duration))

    rps = fill_data(duration, rps_changes)
    terminal_a = Terminal(duration, p_a_changes)
    terminal_b = Terminal(duration, p_b_changes)

    for n, rps_n in enumerate(rps):
        for _ in range(rps_n):
            match bool(terminal_a.beta(n, window) > terminal_b.beta(n, window)):
                case True:
                    terminal_a.sample(n)
                case False:
                    terminal_b.sample(n)

    df = pd.DataFrame(
        {
            "t": t,
            "rps": rps,
            "rps_a": map(
                lambda x, y: x + y,
                terminal_a.count_success,
                terminal_a.count_fail,
            ),
            "rps_b": map(
                lambda x, y: x + y,
                terminal_b.count_success,
                terminal_b.count_fail,
            ),
            "p_a": terminal_a.p,
            "p_b": terminal_b.p,
            "p_success": map(
                lambda x, y: x / y,
                map(
                    lambda x, y: x + y,
                    terminal_a.count_success,
                    terminal_b.count_success,
                ),
                rps,
            ),
        }
    ).set_index("t")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 5))

    df[["p_success", "p_a", "p_b"]].plot(ax=ax1)
    df[["rps", "rps_a", "rps_b"]].plot(ax=ax2)
    plt.show()


if __name__ == "__main__":
    main(
        # Продолжительность симуляции в условных единицах
        duration=60,
        # Окно в котором анализируется статистика
        window=10,
        # Пары момент времени и RPS с этого момента времени
        rps_changes=[
            (0, 100),
        ],
        # Пары момент времени и вероятность конверсии с этого момента времени для терминалов
        p_a_changes=[
            (0, 0.9),
            (20, 0.5),
            (40, 0.9),
        ],
        p_b_changes=[
            (
                0,
                0.8,
            ),
        ],
    )
