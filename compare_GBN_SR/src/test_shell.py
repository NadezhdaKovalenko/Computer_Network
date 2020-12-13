import experiment as expr
import matplotlib.pyplot as plt


def stat_plot(x_list, y_list_gbn, y_list_sr, x_label, y_label, file_name='../results/tmp.png'):
    plt.plot(x_list, y_list_gbn, '-bo', label='gbn')
    plt.plot(x_list, y_list_sr, '-gD', label='sr')
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.legend()
    plt.savefig(file_name)
    plt.close()


def arq_test_shell(
        arg_list: list,
        tries: int,
        arq_mode: str,  # 'gbn' or 'sr'
        test_mode: str,  # 'time' or 'number'
        window_size=-1,
        probability=-1.0,
        session_seconds=-1,
        transfer_packs=-1
) -> list:

    if window_size != -1 and probability != -1:
        raise ValueError

    if test_mode != 'time' and test_mode != 'number':
        raise ValueError

    if arq_mode != 'gbn' and arq_mode != 'sr':
        raise ValueError

    ws, prob = window_size, probability
    output_list = []
    for arg in arg_list:
        result = 0
        for try_expr in range(tries):
            if window_size == -1:
                ws = arg
            else:
                prob = arg

            if test_mode == 'number':
                exp = expr.Experiment(arq_mode, ws, prob, seconds=session_seconds)
                result += exp.calc_efficiency()
            else:
                exp = expr.Experiment(arq_mode, ws, prob, transfer_number=transfer_packs)
                result += exp.calc_time()

        print('done', arg)
        result = int(result / tries)
        output_list.append(result)

    return output_list


def test_pack_lose():
    lose_pr = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]  # lose probability list
    sr_pack = arq_test_shell(lose_pr, 4, 'sr', test_mode='number', window_size=4, session_seconds=20)
    gbn_pack = arq_test_shell(lose_pr, 4, 'gbn', test_mode='number', window_size=4, session_seconds=20)

    stat_plot(lose_pr, gbn_pack, sr_pack,
              'Package lose probability', 'Packages transferred', '../results/pack_lose.png')


def test_pack_window():
    window_size = [1, 2, 3, 4, 6, 8, 10, 12]
    sr_pack = arq_test_shell(window_size, 4, 'sr', test_mode='number', probability=0.15, session_seconds=20)
    gbn_pack = arq_test_shell(window_size,  4, 'gbn', test_mode='number', probability=0.15, session_seconds=20)

    stat_plot(window_size, gbn_pack, sr_pack,
              'Package window size', 'Packages transferred', '../results/pack_window.png')


def test_time_lose():
    lose_pr = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]  # lose probability list
    sr_pack = arq_test_shell(lose_pr, 4, 'sr', test_mode='time', window_size=4, transfer_packs=50)
    gbn_pack = arq_test_shell(lose_pr, 4, 'gbn', test_mode='time', window_size=4, transfer_packs=50)

    stat_plot(lose_pr, gbn_pack, sr_pack,
              'Package lose probability', 'Second for transmission', '../results/time_lose.png')


def test_time_window():
    window_size = [1, 2, 3, 4, 6, 8, 10, 12]
    sr_pack = arq_test_shell(window_size, 4, 'sr', test_mode='time', probability=0.15, transfer_packs=500)
    gbn_pack = arq_test_shell(window_size,  4, 'gbn', test_mode='time', probability=0.15, transfer_packs=500)

    stat_plot(window_size, gbn_pack, sr_pack,
              'Package window size', 'Second for transmission', '../results/time_window.png')


if __name__ == '__main__':
    test_pack_lose()
    test_pack_window()
    test_time_lose()
    test_time_window()
