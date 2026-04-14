## ======================================================
## МИНИ-ИГРА 3 — «ПОСЛЕДОВАТЕЛЬНОСТЬ»
## Файл: minigame3_sequence.rpy
## Вызов: call sequence_minigame
##   mg3_result = True  — прошёл оба раунда
##   mg3_result = False — провалил (открывает концовку 5)
## ======================================================

init python:
    import random as _random

    SEQ_COMMANDS = ["KILL","FLUSH","REVERT","LOCK","PING","RESET","DENY","HALT"]

    ## Длины последовательностей по раундам
    SEQ_LENGTHS = [4, 5]

    def seq_generate(length):
        """Генерирует случайную последовательность команд."""
        return [_random.choice(SEQ_COMMANDS) for _ in range(length)]


## ── Экран ──────────────────────────────────────────────────
##
## ИСПРАВЛЕНИЕ 1:
##   player_seq убран из параметров и объявлен через `default`.
##   Только `default`-переменные поддерживают SetScreenVariable.
##
## ИСПРАВЛЕНИЕ 2:
##   Кнопка «Проверить» теперь возвращает Return(player_seq),
##   что работает только при вызове через renpy.call_screen()
##   (см. label ниже).

screen sequence_screen(round_num=0, correct_seq=None, phase="ready", lives=3, flash_cmd="", message="", msg_color="#aaffaa"):

    ## ── player_seq теперь SCREEN-переменная, SetScreenVariable работает ──
    default player_seq = []

    $ correct_seq = correct_seq if correct_seq is not None else seq_generate(SEQ_LENGTHS[round_num])

    ## ── фон ────────────────────────────────────────────
    add "bg_office"
    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        xsize  780
        ypadding 36
        xpadding 40
        background Frame("gui/frame.png", 20, 20)

        vbox:
            spacing 18

            text "— ПОСЛЕДОВАТЕЛЬНОСТЬ —" xalign 0.5 size 22 color "#ffffff"

            ## статус раунда
            hbox:
                xalign 0.5
                spacing 30
                text "Раунд: {}/{}".format(round_num + 1, len(SEQ_LENGTHS)) size 14 color "#aaaacc"
                text "Жизни: {}".format("♥ " * lives) size 14 color "#ff8888"

            text ("Запомни последовательность команд и повтори её.\nДлина: {} команд.".format(SEQ_LENGTHS[round_num])) xalign 0.5 size 15 color "#cccccc" text_align 0.5

            ## ── прогресс ввода ──
            hbox:
                xalign 0.5
                spacing 8
                for i in range(SEQ_LENGTHS[round_num]):
                    frame:
                        xsize 70
                        ysize 38
                        background "#1a1a2e"
                        xpadding 4
                        ypadding 4
                        text (player_seq[i] if i < len(player_seq) else "·") xalign 0.5 yalign 0.5 size 13 color ("#aaffaa" if i < len(player_seq) else "#444466")

            ## ── сетка команд 4×2 ──
            grid 4 2:
                xalign 0.5
                spacing 10
                for cmd in SEQ_COMMANDS:
                    $ is_flash = (phase == "show" and flash_cmd == cmd)
                    $ is_active = (phase == "input")
                    textbutton cmd:
                        xsize 140
                        ysize 52
                        text_size 16
                        text_xalign 0.5
                        text_yalign 0.5
                        background (
                            "#5555cc" if is_flash else
                            "#1e3a5a" if is_active else
                            "#111128"
                        )
                        hover_background ("#2a4a7a" if is_active else None)
                        text_color ("#ffffff" if is_flash else "#ccddff")
                        sensitive phase == "input"
                        ## SetScreenVariable теперь работает, т.к. player_seq = default
                        action SetScreenVariable("player_seq", player_seq + [cmd])

            ## сообщение
            if message:
                text message xalign 0.5 size 15 color msg_color text_align 0.5

            ## ── кнопки управления ──
            hbox:
                xalign 0.5
                spacing 20

                ## СТАРТ — показать последовательность
                if phase == "ready":
                    textbutton "Показать последовательность":
                        xsize 280
                        ysize 44
                        text_size 15
                        text_xalign 0.5
                        background "#1a3a5a"
                        hover_background "#1e4a70"
                        action Return("show_sequence")

                ## ПРОВЕРИТЬ — возвращает список ответов игрока
                if phase == "input" and len(player_seq) == SEQ_LENGTHS[round_num]:
                    textbutton "Проверить":
                        xsize 180
                        ysize 44
                        text_size 16
                        text_xalign 0.5
                        background "#1a3a5a"
                        hover_background "#1e4a70"
                        ## Возвращаем сам список — label его читает напрямую
                        action Return(player_seq)

                ## СБРОСИТЬ ВВОД
                if phase == "input":
                    textbutton "Сбросить":
                        xsize 140
                        ysize 44
                        text_size 15
                        text_xalign 0.5
                        background "#333355"
                        hover_background "#444477"
                        action SetScreenVariable("player_seq", [])

                ## ПРОДОЛЖИТЬ после результата
                if phase in ("win", "fail", "round_done", "round_retry"):
                    textbutton "Продолжить →":
                        xsize 200
                        ysize 44
                        text_size 16
                        text_xalign 0.5
                        background ("#1a3a1a" if phase in ("win", "round_done") else "#3a1a1a")
                        hover_background ("#2a5a2a" if phase in ("win", "round_done") else "#5a2a2a")
                        action Return("done")


## ── Label-обёртка ──────────────────────────────────────────
##
## ИСПРАВЛЕНИЕ 3:
##   Интерактивные фазы (ready / input / win / fail) используют
##   renpy.call_screen() — блокирующий вызов, при котором Return()
##   корректно возвращает управление в label.
##
##   Анимация показа (phase="show") по-прежнему через
##   renpy.show_screen() + renpy.pause(hard=True) — это правильно.
##
##   Убраны renpy.input() — они показывали поле ввода текста
##   и никак не были связаны с кнопками экрана.

label sequence_minigame:

    python:
        import random as _r
        mg3_result  = False
        lives       = 3
        rounds_done = 0
        seq_lengths = [4, 5]

    label .round_loop:
        python:
            current_length = seq_lengths[rounds_done]
            correct_seq    = [_r.choice(SEQ_COMMANDS) for _ in range(current_length)]

        ## ── 1. READY: ждём нажатия «Показать последовательность» ──
        ## call_screen блокирует выполнение и ждёт Return()
        $ renpy.call_screen(
            "sequence_screen",
            round_num   = rounds_done,
            correct_seq = correct_seq,
            phase       = "ready",
            lives       = lives,
            message     = "",
        )

        ## ── 2. SHOW: анимируем подсветку команд ──
        ## show_screen + pause(hard=True) — правильный способ
        python:
            for cmd in correct_seq:
                renpy.show_screen(
                    "sequence_screen",
                    round_num   = rounds_done,
                    correct_seq = correct_seq,
                    phase       = "show",
                    flash_cmd   = cmd,
                    lives       = lives,
                    message     = "Запоминай...",
                )
                renpy.pause(0.7, hard=True)
                renpy.show_screen(
                    "sequence_screen",
                    round_num   = rounds_done,
                    correct_seq = correct_seq,
                    phase       = "show",
                    flash_cmd   = "",
                    lives       = lives,
                    message     = "",
                )
                renpy.pause(0.25, hard=True)
            renpy.hide_screen("sequence_screen")

        ## ── 3. INPUT: ждём ввода игрока ──
        ## call_screen вернёт список команд (Return(player_seq))
        $ player_seq = renpy.call_screen(
            "sequence_screen",
            round_num   = rounds_done,
            correct_seq = correct_seq,
            phase       = "input",
            lives       = lives,
            message     = "Твоя очередь. Повтори последовательность.",
        )

        ## ── 4. Проверка результата ──
        python:
            _round_passed    = False
            _game_over_fail  = False

            if player_seq == correct_seq:
                rounds_done += 1
                if rounds_done >= len(seq_lengths):
                    mg3_result = True        ## победа в игре
                else:
                    _round_passed = True     ## раунд пройден, следующий
            else:
                lives -= 1
                if lives <= 0:
                    _game_over_fail = True   ## жизни кончились

        ## ── 5. Показываем итог и переходим дальше ──

        if mg3_result:
            $ renpy.call_screen(
                "sequence_screen",
                round_num   = rounds_done - 1,
                correct_seq = correct_seq,
                phase       = "win",
                lives       = lives,
                message     = "Скрипт остановлен! Данные заблокированы.",
                msg_color   = "#aaffaa",
            )
            jump .done

        elif _game_over_fail:
            $ renpy.call_screen(
                "sequence_screen",
                round_num   = rounds_done,
                correct_seq = correct_seq,
                phase       = "fail",
                lives       = 0,
                message     = "Попытки исчерпаны. Данные ушли к Орлову.",
                msg_color   = "#ffaaaa",
            )
            jump .done

        elif _round_passed:
            ## Раунд пройден — показываем сообщение, затем следующий раунд
            $ renpy.call_screen(
                "sequence_screen",
                round_num   = rounds_done,
                correct_seq = correct_seq,
                phase       = "round_done",
                lives       = lives,
                message     = "Раунд пройден! Следующий.",
                msg_color   = "#aaffaa",
            )
            jump .round_loop

        else:
            ## Неверно, жизни ещё есть — повторяем раунд заново
            $ renpy.call_screen(
                "sequence_screen",
                round_num   = rounds_done,
                correct_seq = correct_seq,
                phase       = "round_retry",
                lives       = lives,
                message     = "Неверно. Попробуй ещё раз. Жизней: {}.".format(lives),
                msg_color   = "#ffaaaa",
            )
            jump .round_loop

    label .done:
        return


## ── Пример вызова в script.rpy ────────────────────────────
##
##   label scene_2_2:
##       call sequence_minigame
##       if mg3_result:
##           "Алекс: Скрипт остановлен. Данные заблокированы."
##           jump act3_start
##       else:
##           "Алекс: Поздно. Часть данных ушла к Орлову."
##           $ ending_5_unlocked = True
##           jump act3_start
