## ======================================================
## МИНИ-ИГРА 1 — «ДЕШИФРОВКА»
## Файл: minigame1_cipher.rpy
## Вызов из сценария: $ result = renpy.call_screen("cipher_screen")
##   result = True  — игрок решил
##   result = False — провалил (3 попытки)
## ======================================================

init python:
    import random

    ## Пул букв и правильный ответ
    CIPHER_POOL   = ["Э","Т","Н","Д","Ь","Г","И","Е","О","Н","Е","И"]
    CIPHER_ANSWER = ["Э","Т","Н","Д"]

    def cipher_check(selected):
        return selected == CIPHER_ANSWER


screen cipher_screen():

    ## ── состояние ──────────────────────────────────────
    default pool_order  = sorted(CIPHER_POOL, key=lambda x: renpy.random.random())
    default selected    = []          # буквы в слотах (макс 4)
    default attempts    = 3
    default message     = ""
    default msg_color   = "#aaffaa"
    default solved      = False
    default failed      = False

    ## ── фон ────────────────────────────────────────────
    add "bg_office"                   ## замени на свой фон

    ## ── затемнение ─────────────────────────────────────
    add Solid("#00000099")

    ## ── окно игры ──────────────────────────────────────
    frame:
        xalign 0.5
        yalign 0.5
        xsize 780
        ypadding 36
        xpadding 40
        background Frame("gui/frame.png", 20, 20)   ## замени при необходимости

        vbox:
            spacing 20

            ## заголовок
            text "— ДЕШИФРОВКА —" xalign 0.5 size 22 color "#ffffff"

            text "Хакер оставил зашифрованный фрагмент в логах.\nВыбери 4 буквы в правильном порядке.":
                xalign 0.5
                size 16
                color "#cccccc"
                text_align 0.5

            ## ── слоты ответа ──
            hbox:
                xalign 0.5
                spacing 12
                for i in range(4):
                    frame:
                        xsize 70
                        ysize 70
                        background "#1a1a2e"
                        xpadding 0
                        ypadding 0
                        text (selected[i] if i < len(selected) else "?"):
                            xalign 0.5
                            yalign 0.5
                            size 28
                            color "#e0e0ff"

            ## ── пул букв ──
            hbox:
                xalign 0.5
                spacing 8
                for idx, letter in enumerate(pool_order):
                    ## серая кнопка если уже выбрана
                    $ already = selected.count(letter) >= CIPHER_POOL.count(letter)
                    textbutton letter:
                        xsize 52
                        ysize 52
                        text_size 22
                        text_xalign 0.5
                        text_yalign 0.5
                        background ("#444466" if already else "#2a2a4a")
                        hover_background "#555588"
                        text_color ("#666677" if already else "#ffffff")
                        sensitive not already and len(selected) < 4 and not solved and not failed
                        action [
                            SetScreenVariable("selected", selected + [letter]),
                            SetScreenVariable("message", ""),
                        ]

            ## ── кнопки управления ──
            hbox:
                xalign 0.5
                spacing 20

                ## сброс
                textbutton "Очистить":
                    xsize 160
                    ysize 44
                    text_size 16
                    text_xalign 0.5
                    background "#333355"
                    hover_background "#444477"
                    sensitive not solved and not failed
                    action [
                        SetScreenVariable("selected", []),
                        SetScreenVariable("message", ""),
                    ]

                ## проверить
                textbutton "Проверить":
                    xsize 160
                    ysize 44
                    text_size 16
                    text_xalign 0.5
                    background "#1a3a5a"
                    hover_background "#1e4a70"
                    sensitive len(selected) == 4 and not solved and not failed
                    action If(
                        cipher_check(selected),
                        ## верно
                        [
                            SetScreenVariable("message", "Верно! «ЭТНД» — Это Не Деньги. Мотив раскрыт."),
                            SetScreenVariable("msg_color", "#aaffaa"),
                            SetScreenVariable("solved", True),
                        ],
                        ## неверно
                        If(
                            attempts > 1,
                            [
                                SetScreenVariable("attempts", attempts - 1),
                                SetScreenVariable("selected", []),
                                SetScreenVariable("message",
                                    "Неверно. Осталось попыток: {}. Попробуй снова.".format(attempts - 1)),
                                SetScreenVariable("msg_color", "#ffaaaa"),
                            ],
                            [
                                SetScreenVariable("attempts", 0),
                                SetScreenVariable("message",
                                    "Попытки исчерпаны. Смысл послания прояснится позже..."),
                                SetScreenVariable("msg_color", "#ffaaaa"),
                                SetScreenVariable("failed", True),
                            ]
                        )
                    )

            ## сообщение
            if message:
                text message xalign 0.5 size 15 color msg_color text_align 0.5

            ## попытки
            if not solved and not failed:
                text "Попытки: {}".format(attempts) xalign 0.5 size 13 color "#888888"

            ## кнопка продолжить (после решения или провала)
            if solved or failed:
                textbutton "Продолжить →":
                    xalign 0.5
                    xsize 200
                    ysize 44
                    text_size 16
                    text_xalign 0.5
                    background ("#1a3a1a" if solved else "#3a1a1a")
                    hover_background ("#2a5a2a" if solved else "#5a2a2a")
                    action Return(solved)


## ── Вызов из сценария ──────────────────────────────
## Пример использования в script.rpy:
##
##   label minigame1_call:
##       $ mg1_result = renpy.call_screen("cipher_screen")
##       if mg1_result:
##           $ evidence = True
##           "Алекс: Это Не Деньги. Он что-то ищет."
##       else:
##           $ trust -= 1
##           "Алекс: Не получилось. Разберёмся позже."
##       jump act2_start
