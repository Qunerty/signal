## ======================================================
## МИНИ-ИГРА 2 — «СОПОСТАВЛЕНИЕ»
## Файл: minigame2_match.rpy
## Вызов: $ result = renpy.call_screen("match_screen")
##   result = True  — все пары верны
##   result = False — есть ошибки (trust -1 применяй снаружи)
## ======================================================

init python:

    ## Правильные пары: левый элемент -> правый элемент
    MATCH_PAIRS = {
        "VPN-шлюз"        : "Входящий туннель",
        "Архивный сервер" : "Чтение файлов",
        "Почтовый сервер" : "Прикрытие трафика",
        "Сервер логов"    : "Удаление следов",
    }

    ## Фиксированный порядок левого столбца
    MATCH_LEFT  = list(MATCH_PAIRS.keys())

    def match_all_correct(user_dict):
        """Возвращает True если все соединения совпадают с правильными."""
        if len(user_dict) != len(MATCH_PAIRS):
            return False
        for left, right in user_dict.items():
            if MATCH_PAIRS.get(left) != right:
                return False
        return True

    def match_count_errors(user_dict):
        errors = 0
        for left, right in user_dict.items():
            if MATCH_PAIRS.get(left) != right:
                errors += 1
        return errors


screen match_screen():

    ## ── состояние ──────────────────────────────────────
    default right_order   = sorted(list(MATCH_PAIRS.values()),
                                   key=lambda x: renpy.random.random())
    default active_left   = None      # выбранный левый узел
    default connections   = {}        # {left: right}
    default submitted     = False
    default all_ok        = False
    default message       = ""
    default msg_color     = "#aaffaa"

    ## ── фон ────────────────────────────────────────────
    add "bg_office"
    add Solid("#00000099")

    ## ── окно ───────────────────────────────────────────
    frame:
        xalign 0.5
        yalign 0.5
        xsize  820
        ypadding 36
        xpadding 40
        background Frame("gui/frame.png", 20, 20)

        vbox:
            spacing 18

            text "— СОПОСТАВЛЕНИЕ —" xalign 0.5 size 22 color "#ffffff"

            text ("Нажми узел слева, затем действие справа.\n" "Определи цепочку проникновения, чтобы заблокировать без потерь.") xalign 0.5 size 15 color "#cccccc" text_align 0.5

            ## ── два столбца ──
            hbox:
                xalign 0.5
                spacing 60

                ## левый столбец — узлы
                vbox:
                    spacing 10
                    text "Узел сети" xalign 0.5 size 13 color "#888888"
                    for node in MATCH_LEFT:
                        $ is_connected  = node in connections
                        $ is_active     = active_left == node
                        $ is_wrong      = submitted and is_connected and connections[node] != MATCH_PAIRS[node]
                        $ is_correct    = submitted and is_connected and connections[node] == MATCH_PAIRS[node]
                        textbutton node:
                            xsize 190
                            ysize 50
                            text_size 15
                            text_xalign 0.5
                            text_yalign 0.5
                            background (
                                "#2a5a2a" if is_correct else
                                "#5a1a1a" if is_wrong   else
                                "#1a3a5a" if is_active  else
                                "#2a2a4a" if is_connected else
                                "#1a1a2e"
                            )
                            hover_background ("#333366" if not submitted else None)
                            text_color (
                                "#aaffaa" if is_correct else
                                "#ffaaaa" if is_wrong   else
                                "#aaccff" if is_active  else
                                "#cccccc"
                            )
                            sensitive not submitted
                            action [
                                SetScreenVariable("active_left", None if is_active else node),
                            ]

                ## стрелки (текст-заглушка, в реальном Ren'Py можно добавить линии через displayable)
                vbox:
                    yalign 0.5
                    spacing 10
                    for node in MATCH_LEFT:
                        $ arrow_text = "→ {}".format(connections[node]) if node in connections else "···"
                        text arrow_text yalign 0.5 size 13 color "#666688" ysize 50 yoffset 15

                ## правый столбец — действия
                vbox:
                    spacing 10
                    text "Действие" xalign 0.5 size 13 color "#888888"
                    for action_name in right_order:
                        ## уже использована?
                        $ used_by     = [l for l, r in connections.items() if r == action_name]
                        $ is_taken    = len(used_by) > 0
                        $ owner       = used_by[0] if is_taken else None
                        $ is_corr_r   = submitted and is_taken and MATCH_PAIRS.get(owner) == action_name
                        $ is_wrong_r  = submitted and is_taken and MATCH_PAIRS.get(owner) != action_name
                        textbutton action_name:
                            xsize 190
                            ysize 50
                            text_size 15
                            text_xalign 0.5
                            text_yalign 0.5
                            background (
                                "#2a5a2a" if is_corr_r  else
                                "#5a1a1a" if is_wrong_r else
                                "#2a2a4a" if is_taken   else
                                "#1a1a2e"
                            )
                            hover_background ("#333366" if not submitted else None)
                            text_color (
                                "#aaffaa" if is_corr_r  else
                                "#ffaaaa" if is_wrong_r else
                                "#aaaacc" if is_taken   else
                                "#ffffff"
                            )
                            sensitive active_left is not None and not submitted
                            action If(
                                active_left is not None,
                                [
                                    ## если правый уже занят — переназначаем
                                    If(is_taken,
                                        SetDict(connections, owner, None),   # убираем старую связь
                                    ),
                                    SetDict(connections, active_left, action_name),
                                    SetScreenVariable("active_left", None),
                                ]
                            )

            ## ── кнопки управления ──
            hbox:
                xalign 0.5
                spacing 20

                textbutton "Сбросить":
                    xsize 160
                    ysize 44
                    text_size 16
                    text_xalign 0.5
                    background "#333355"
                    hover_background "#444477"
                    sensitive not submitted
                    action [
                        SetScreenVariable("connections", {}),
                        SetScreenVariable("active_left", None),
                        SetScreenVariable("message", ""),
                    ]

                textbutton "Подтвердить":
                    xsize 160
                    ysize 44
                    text_size 16
                    text_xalign 0.5
                    background "#1a3a5a"
                    hover_background "#1e4a70"
                    sensitive len(connections) == len(MATCH_LEFT) and not submitted
                    action [
                        SetScreenVariable("submitted", True),
                        SetScreenVariable("all_ok", match_all_correct(connections)),
                        SetScreenVariable("message",
                            "Точка входа найдена. Блокировка пройдёт без потерь."
                            if match_all_correct(connections) else
                            "Есть ошибки. Часть файлов успела уйти."
                        ),
                        SetScreenVariable("msg_color",
                            "#aaffaa" if match_all_correct(connections) else "#ffaaaa"),
                    ]

            if message:
                text message xalign 0.5 size 15 color msg_color text_align 0.5

            if submitted:
                textbutton "Продолжить →":
                    xalign 0.5
                    xsize 200
                    ysize 44
                    text_size 16
                    text_xalign 0.5
                    background ("#1a3a1a" if all_ok else "#3a1a1a")
                    hover_background ("#2a5a2a" if all_ok else "#5a2a2a")
                    action Return(all_ok)


## ── Вызов из сценария ──────────────────────────────
## Пример использования в script.rpy:
##
##   label minigame2_call:
##       $ mg2_result = renpy.call_screen("match_screen")
##       if mg2_result:
##           "Рита: Точка входа найдена. Можно заблокировать без потерь."
##       else:
##           $ trust -= 1
##           "Алекс: Ошибка. Несколько файлов уже скопированы."
##       jump scene_2_2
