import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import json
import os


class BlackjackGame:
    """
    21点游戏类

    该类实现了21点（Blackjack）游戏的逻辑和用户界面。用户可以通过界面进行下注、要牌、停牌、加倍等操作。
    游戏支持保存和加载游戏进度，最多可以保存三个不同的存档。

    属性:
        master (tk.Tk): Tkinter主窗口对象。
        player_money (float): 玩家当前的资金。
        bet (float): 玩家当前的下注金额。
        player_hand (list): 玩家的手牌列表。
        ai_hand (list): AI的手牌列表。
        deck (list): 当前的牌组。
        game_started (bool): 游戏是否已经开始。
        player_turn (bool): 当前是否是玩家的回合。
        player_is_dealer (bool): 玩家是否为庄家。
        current_save (str): 当前使用的存档名称。
        game_ended (bool): 游戏是否已经结束。
        player_stood (bool): 玩家是否已经停牌。
        ai_stood (bool): AI是否已经停牌。
        save_manager_window (tk.Toplevel): 存档管理窗口对象。
        save_path (str): 存档文件的路径。

    方法:
        create_widgets: 创建游戏界面组件。
        log_game_action: 记录游戏中的某个操作到日志中。
        get_money_text: 获取显示玩家资金的文本。
        get_bet_text: 获取显示当前下注金额的文本。
        update_labels: 更新显示玩家资金和下注金额的标签。
        place_bet: 玩家下注指定金额。
        all_in: 玩家全押。
        reset_bet: 重置玩家的下注。
        start_game: 开始新的一局游戏。
        create_deck: 创建一副新的牌组。
        draw_card: 从牌组中随机抽取一张牌。
        calculate_hand_value: 计算手牌的点数。
        update_card_labels: 更新显示玩家和AI手牌的文本。
        hit: 玩家要牌。
        ai_turn: AI的回合逻辑。
        _ai_turn_logic: AI的具体要牌逻辑。
        stand: 玩家停牌。
        double_down: 玩家加倍下注。
        check_game_end: 检查游戏是否结束。
        determine_winner: 判断游戏的胜负。
        end_game: 结束游戏并处理结果。
        game_over: 处理玩家资金用完的情况。
        update_game_buttons: 更新游戏控制按钮的状态。
        save_game: 保存当前游戏状态到指定存档。
        load_game: 加载第一个存档。
        load_saves: 加载所有存档。
        show_save_manager: 显示存档管理窗口。
        load_save: 加载指定存档。
        delete_save: 删除指定存档。
        save_to_new: 创建新的存档。
    """

    def __init__(self, master):
        self.master = master
        self.master.title("21点游戏")
        self.master.geometry("800x600")

        self.player_money = 2000.00
        self.bet = 0
        self.player_hand = []
        self.ai_hand = []
        self.deck = []
        self.game_started = False
        self.player_turn = True
        self.player_is_dealer = False
        self.current_save = "无"
        self.game_ended = False
        self.player_stood = False
        self.ai_stood = False
        self.save_manager_window = None

        self.save_path = os.path.join(os.path.dirname(__file__),
                                      "blackjack_saves.json")

        self.create_widgets()
        self.load_game()

    def create_widgets(self):
        # 设置主窗口的字体
        self.master.option_add("*Font", "Arial 12")
        self.master.option_add("*Font", "SIMHEI 12")

        # 创建左侧框架，用于放置游戏控制按钮和标签
        left_frame = tk.Frame(self.master)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # 显示玩家当前资金的标签
        self.money_label = tk.Label(left_frame, text=self.get_money_text())
        self.money_label.pack()

        # 显示当前游戏存档名称的标签
        self.current_save_label = tk.Label(left_frame,
                                           text=f"当前存档: {self.current_save}")
        self.current_save_label.pack()

        # 创建放置赌注按钮的框架
        self.bet_frame = tk.Frame(left_frame)
        self.bet_frame.pack()

        # 筹码面额数组
        self.chips = [1, 10, 100, 1000, 10000, 100000]
        # 保存押注按钮对象
        self.bet_buttons = []
        # 创建并添加不同面额的筹码按钮
        for chip in self.chips:
            btn = tk.Button(self.bet_frame,
                            text=f"${chip}",
                            command=lambda x=chip: self.place_bet(x))
            btn.pack()
            self.bet_buttons.append((chip, btn))

        # 添加“ALL IN”和“重置”按钮
        tk.Button(self.bet_frame, text="ALL IN", command=self.all_in).pack()
        tk.Button(self.bet_frame, text="重置", command=self.reset_bet).pack()

        # 显示当前赌注的标签
        self.bet_label = tk.Label(left_frame, text=self.get_bet_text())
        self.bet_label.pack()

        # 创建游戏控制按钮，包括开始游戏、要牌、停牌、加倍和保存/加载游戏
        self.game_buttons = {
            "start":
            tk.Button(left_frame,
                      text="开始游戏",
                      command=self.start_game,
                      state=tk.NORMAL),
            "hit":
            tk.Button(left_frame,
                      text="要牌",
                      command=self.hit,
                      state=tk.DISABLED),
            "stand":
            tk.Button(left_frame,
                      text="停牌",
                      command=self.stand,
                      state=tk.DISABLED),
            "double":
            tk.Button(left_frame,
                      text="加倍",
                      command=self.double_down,
                      state=tk.DISABLED),
            "save_load":
            tk.Button(left_frame,
                      text="保存/加载游戏",
                      command=self.show_save_manager,
                      state=tk.NORMAL)
        }

        # 将游戏控制按钮添加到左侧框架
        for button in self.game_buttons.values():
            button.pack()

        # 创建右侧框架，用于显示游戏日志
        right_frame = tk.Frame(self.master)
        right_frame.pack(side=tk.RIGHT,
                         padx=10,
                         pady=10,
                         fill=tk.BOTH,
                         expand=True)

        # 创建并添加游戏日志文本框，初始状态为只读
        self.game_log = scrolledtext.ScrolledText(right_frame,
                                                  wrap=tk.WORD,
                                                  width=50,
                                                  height=30,
                                                  font=("SIMSUN", 16))
        self.game_log.pack(fill=tk.BOTH, expand=True)
        self.game_log.config(state=tk.DISABLED)

    def log_game_action(self, action):
        self.game_log.config(state=tk.NORMAL)

        # 插入新日志
        self.game_log.insert(tk.END, action + "\n")
        self.game_log.see(tk.END)

        # 移除旧的加粗
        self.game_log.tag_remove("bold_last", "1.0", tk.END)

        # 查找最后一段起始位置
        text = self.game_log.get("1.0", tk.END)
        lines = text.rstrip("\n").split("\n")
        idx = len(lines) - 1
        while idx > 0 and lines[idx].strip() == "":
            idx -= 1
        # 向上找到空行
        start_idx = idx
        while start_idx > 0 and lines[start_idx - 1].strip() != "":
            start_idx -= 1
        # 计算tag范围
        char_start = f"{start_idx + 1}.0"
        char_end = f"{idx + 1}.end"

        # 设置加粗tag
        self.game_log.tag_add("bold_last", char_start, char_end)
        self.game_log.tag_configure("bold_last", font=("SIMSUN", 16, "bold"))

        self.game_log.config(state=tk.DISABLED)

    def get_money_text(self):
        return f"资金: ${self.player_money:.2f}"

    def get_bet_text(self):
        return f"当前下注: ${self.bet:.2f}"

    def update_labels(self):
        self.money_label.config(text=self.get_money_text())
        self.bet_label.config(text=self.get_bet_text())
        self.update_bet_buttons()

    def place_bet(self, amount):
        if not self.game_started and amount <= self.player_money:
            self.bet += amount
            self.player_money -= amount
            self.update_labels()
            self.log_game_action(f"下注 ${amount:.2f}")

    def all_in(self):
        if not self.game_started:
            self.reset_bet()
            self.bet = self.player_money
            self.player_money = 0
            self.update_labels()
            self.log_game_action(f"全押 ${self.bet:.2f}")

    def reset_bet(self):
        if not self.game_started:
            self.player_money += self.bet
            self.bet = 0
            self.update_labels()
            self.log_game_action("\n重置下注\n")

    def start_game(self):
        if self.bet == 0:
            messagebox.showwarning("警告", "请先下注")
            return

        self.game_started = True
        self.game_ended = False
        self.deck = self.create_deck()
        self.player_hand = []
        self.ai_hand = []
        self.player_is_dealer = random.choice([True, False])
        self.player_turn = self.player_is_dealer

        self.log_game_action("\n*****·*****·*****\n")
        self.log_game_action("新一局游戏开始\n")
        self.log_game_action(
            f">>> 【{'玩家' if self.player_is_dealer else 'AI'}】为庄家<<<\n")
        self.player_stood = False
        self.ai_stood = False

        # 每个玩家抽两张牌
        for _ in range(2):
            self.player_hand.append(self.draw_card())
            self.ai_hand.append(self.draw_card())

        self.update_card_labels()
        self.log_game_action(">> 发牌完成\n")

        # 检查是否有人获得黑杰克
        player_value = self.calculate_hand_value(self.player_hand)
        ai_value = self.calculate_hand_value(self.ai_hand)

        if player_value == 21 and ai_value == 21:
            self.end_game("<$> 双方获得黑杰克，平局！\n")
        elif player_value == 21:
            self.end_game("<$> 玩家获得黑杰克，玩家胜利！\n")
        elif ai_value == 21:
            self.end_game("<$> AI获得黑杰克，AI胜利！\n")
        else:
            self.update_game_buttons()
            if not self.player_turn:
                self.log_game_action("*-> AI先手回合：\n")
                self.ai_turn()
            else:
                self.log_game_action("*-> 玩家先手回合：\n")

    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = [
            'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'
        ]
        return [f"{rank}{suit}" for suit in suits for rank in ranks]

    def draw_card(self):
        return self.deck.pop(random.randint(0, len(self.deck) - 1))

    def calculate_hand_value(self, hand):
        value = sum(
            10 if rank in ['J', 'Q', 'K'] else 11 if rank == 'A' else int(rank)
            for rank in [card[:-1] for card in hand])
        aces = sum(1 for card in hand if card[0] == 'A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def update_card_labels(self):
        player_text = f"> {'庄家' if self.player_is_dealer else '闲家'}手牌: {' '.join(self.player_hand)} (点数: {self.calculate_hand_value(self.player_hand)})"
        self.log_game_action(player_text)

        ai_text = f"> {'闲家' if self.player_is_dealer else '庄家'}手牌: {' '.join(self.ai_hand)} (点数: {self.calculate_hand_value(self.ai_hand)})"
        self.log_game_action(ai_text)

    def hit(self):
        if self.game_ended or self.player_stood or not self.player_turn:
            self.check_game_end()
            return

        if self.player_turn:
            self.player_hand.append(self.draw_card())
            self.update_card_labels()
            self.game_buttons["double"].config(state=tk.DISABLED)
            self.log_game_action(">>> 玩家要牌\n")

            player_value = self.calculate_hand_value(self.player_hand)
            if player_value > 21:
                self.end_game("<$> 玩家爆牌，AI胜利！\n")
            elif player_value == 21:
                self.end_game("<$> 玩家达到21点，玩家胜利！\n")
            else:
                self.player_turn = False
                self.ai_turn()
        else:
            self.ai_turn()

    def ai_turn(self):
        # 加入1秒延时后再执行 AI 的动作
        self.master.after(1000, self._ai_turn_logic)

    def _ai_turn_logic(self):
        if self.ai_stood:
            self.check_game_end()
            return

        ai_value = self.calculate_hand_value(self.ai_hand)
        if ai_value < 17:
            self.ai_hand.append(self.draw_card())
            self.update_card_labels()
            self.log_game_action(">>> AI要牌\n")
            new_ai_value = self.calculate_hand_value(self.ai_hand)
            if new_ai_value > 21:
                self.end_game("<$> AI爆牌，玩家胜利！\n")
            elif new_ai_value == 21:
                self.ai_stood = True
                self.end_game("<$> AI达到21点，AI胜利！\n")
                self.check_game_end()
            elif not self.player_stood:
                self.player_turn = True
                self.update_game_buttons()
            else:
                self.ai_turn()
        else:
            self.ai_stood = True
            self.log_game_action("=!= AI停牌\n")
            self.check_game_end()

    def stand(self):
        if self.game_ended:
            return

        if self.player_turn:
            self.player_stood = True
            self.player_turn = False
            self.update_game_buttons()
            self.log_game_action("=!= 玩家停牌\n")
            self.ai_turn()
        else:
            self.ai_stood = True
            self.log_game_action("=!= AI停牌\n")
            self.check_game_end()

    def double_down(self):
        if self.game_ended or self.player_money < self.bet:
            self.log_game_action("资金不足，无法加倍。\n")
            return

        self.player_money -= self.bet
        self.bet *= 2
        self.update_labels()
        self.log_game_action(f">>> 玩家加倍，当前下注: ${self.bet:.2f}\n")

        # 玩家加倍后自动抽一张牌
        self.player_hand.append(self.draw_card())
        self.update_card_labels()
        self.log_game_action(">>> 加倍后自动抽牌\n")

        player_value = self.calculate_hand_value(self.player_hand)
        if player_value > 21:
            self.end_game("<$> 玩家爆牌，AI胜利！\n")
        elif player_value == 21:
            self.end_game("<$> 玩家达到21点，玩家胜利！\n")
        else:
            # 强制玩家停牌，不允许继续抽牌
            self.player_stood = True
            self.player_turn = False
            self.update_game_buttons()
            self.log_game_action("=!= 玩家已加倍，现在停牌\n")
            self.ai_turn()

    def check_game_end(self):
        if self.player_stood and self.ai_stood:
            self.end_game(self.determine_winner())
        elif self.player_stood:
            self.ai_turn()
        elif self.ai_stood:
            self.player_turn = True
            self.update_game_buttons()

    def determine_winner(self):
        player_value = self.calculate_hand_value(self.player_hand)
        ai_value = self.calculate_hand_value(self.ai_hand)

        if ai_value > 21:
            return "<$> AI爆牌，玩家胜利！\n"
        elif player_value > ai_value:
            return "<$> 玩家胜利！\n"
        elif player_value < ai_value:
            return "<$> AI胜利！\n"
        else:
            return "<$> 平局！\n"

    def end_game(self, result):
        self.game_started = False
        self.game_ended = True
        self.update_card_labels()
        self.log_game_action(result)

        if "玩家胜利" in result:
            if "黑杰克" in result:
                win_amount = self.bet * 3
                self.log_game_action(f"<<<$>>> 黑杰克！玩家赢得 ${win_amount:.2f}\n")
            else:
                win_amount = self.bet * 2
                self.log_game_action(f"<$> 玩家赢得 ${win_amount:.2f}\n")
            self.player_money += win_amount
        elif "平局" in result:
            self.player_money += self.bet
            self.log_game_action(f"退回下注 ${self.bet:.2f}\n")

        self.bet = 0
        self.update_labels()
        self.update_game_buttons()

        if self.player_money <= 0:
            self.game_over()

    def game_over(self):
        messagebox.showinfo("游戏结束", "你的资金已经用完，游戏结束！")
        self.show_save_manager(disable_save=True)

    def update_game_buttons(self):
        if self.game_started and not self.game_ended:
            states = {
                "start":
                tk.DISABLED,
                "hit":
                tk.NORMAL if self.player_turn else tk.DISABLED,
                "stand":
                tk.NORMAL if self.player_turn else tk.DISABLED,
                "double":
                tk.NORMAL if self.player_turn and len(self.player_hand) == 2
                else tk.DISABLED,
                "save_load":
                tk.DISABLED
            }
        else:
            states = {
                "start": tk.NORMAL,
                "hit": tk.DISABLED,
                "stand": tk.DISABLED,
                "double": tk.DISABLED,
                "save_load": tk.NORMAL
            }

        for button_name, state in states.items():
            self.game_buttons[button_name].config(
                state=(tk.NORMAL if state == 'normal' else tk.
                       ACTIVE if state == 'active' else tk.DISABLED))

    def update_bet_buttons(self):
        for chip, btn in self.bet_buttons:
            if self.player_money < chip or self.game_started:
                btn.config(state=tk.DISABLED)
            else:
                btn.config(state=tk.NORMAL)

    def save_game(self, save_name):
        saves = self.load_saves()
        saves[save_name] = self.player_money
        with open(self.save_path, "w", encoding='utf-8') as f:
            json.dump(saves, f)
        messagebox.showinfo("保存成功", f"游戏已保存到 {save_name}")
        self.current_save = save_name
        self.current_save_label.config(text=f"当前存档: {save_name}")
        if self.save_manager_window:
            self.save_manager_window.destroy()

    def load_game(self):
        saves = self.load_saves()
        if saves:
            first_save = list(saves.keys())[0]
            self.load_save(first_save)

    def load_saves(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, "r", encoding='utf-8') as f:
                return json.load(f)
        return {}

    def show_save_manager(self, disable_save=False):
        saves = self.load_saves()
        self.save_manager_window = tk.Toplevel(self.master)
        self.save_manager_window.title("存档管理")
        self.save_manager_window.geometry("400x300")

        for save_name, funds in saves.items():
            frame = tk.Frame(self.save_manager_window)
            frame.pack(fill=tk.X)

            tk.Label(frame,
                     text=f"{save_name}: ${funds:.2f}").pack(side=tk.LEFT,
                                                             padx=5,
                                                             pady=5)

            for button_text, command, state in [
                ("加载", lambda name=save_name: self.load_save(name), tk.NORMAL),
                ("覆盖", lambda name=save_name: self.save_game(name),
                 tk.DISABLED if disable_save else tk.NORMAL),
                ("删除", lambda name=save_name: self.delete_save(name),
                 tk.NORMAL)
            ]:
                tk.Button(
                    frame,
                    text=button_text,
                    command=command,
                    state=tk.NORMAL if state == 'normal' else
                    tk.ACTIVE if state == 'active' else tk.DISABLED).pack(
                        side=tk.LEFT, padx=5, pady=5)

        if len(saves) < 3 and not disable_save:
            tk.Button(self.save_manager_window,
                      text="+",
                      command=self.save_to_new).pack(pady=10)

    def load_save(self, save_name):
        saves = self.load_saves()
        if save_name in saves:
            self.player_money = saves[save_name]
            self.bet = 0
            self.game_started = False
            self.update_labels()
            self.current_save = save_name
            self.current_save_label.config(text=f"当前存档: {save_name}")
            messagebox.showinfo("加载成功", f"已加载存档 {save_name}")
            if hasattr(self, 'save_manager_window'):
                if self.save_manager_window:
                    self.save_manager_window.destroy()

    def delete_save(self, save_name):
        if messagebox.askyesno("删除存档", f"确定要删除存档 {save_name} 吗？"):
            saves = self.load_saves()
            if save_name in saves:
                del saves[save_name]
                sorted_saves = {}
                save_names = ["存档1", "存档2", "存档3"]
                for i, key in enumerate(saves.keys()):
                    sorted_saves[save_names[i]] = saves[key]
                with open(self.save_path, "w", encoding='utf-8') as f:
                    json.dump(sorted_saves, f)
                messagebox.showinfo("删除成功", f"存档 {save_name} 已删除")
                if self.save_manager_window:
                    self.save_manager_window.destroy()
                self.show_save_manager()

    def save_to_new(self):
        save_window = tk.Toplevel(self.master)
        save_window.title("新建存档")
        save_window.geometry("300x150")

        tk.Label(save_window, text="你想要新的存档为：").pack(pady=10)

        def save_current():
            saves = self.load_saves()
            save_names = ["存档1", "存档2", "存档3"]
            available_save_name = next(
                (name for name in save_names if name not in saves), None)

            if available_save_name:
                self.save_game(available_save_name)
            else:
                messagebox.showwarning("警告", "存档数量已达上限")
            if self.save_manager_window:
                self.save_manager_window.destroy()
            save_window.destroy()

        def create_new():
            saves = self.load_saves()
            save_names = ["存档1", "存档2", "存档3"]
            available_save_name = next(
                (name for name in save_names if name not in saves), None)

            if available_save_name:
                saves[available_save_name] = 2000.00
                with open(self.save_path, "w", encoding='utf-8') as f:
                    json.dump(saves, f)
                messagebox.showinfo("新建存档成功", f"新存档已创建: {available_save_name}")
                self.current_save = available_save_name
                self.current_save_label.config(
                    text=f"当前存档: {available_save_name}")
                if self.save_manager_window:
                    self.save_manager_window.destroy()
            else:
                messagebox.showwarning("警告", "存档数量已达上限")
            save_window.destroy()

        tk.Button(save_window, text="保存当前存档",
                  command=save_current).pack(pady=5)
        tk.Button(save_window, text="新建存档", command=create_new).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()
