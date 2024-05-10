import pulp


class VertiportLP:
    def __init__(self, weight):
        self.max_fato_uam = 4
        self.max_path_in_uam = 6
        self.max_gate_uam = 8
        self.max_path_out_uam = 6
        self.max_waiting_room_psg = 100

        self.current_fato_in_uam = 2
        self.current_path_in_uam = 6
        self.current_gate_uam = 3
        self.current_path_out_uam = 2
        self.current_fato_out_uam = 0
        self.current_gate_uam_psg = 7
        self.current_waiting_room_psg = 40
        self.weight = weight

        # 의사결정 변수
        self.x_fato_in_uam = pulp.LpVariable('fato_in_uam', lowBound=0, upBound=self.max_fato_uam, cat='Integer')
        self.x_path_in_uam = pulp.LpVariable('path_in_uam', lowBound=0, upBound=self.max_path_in_uam, cat='Integer')
        self.x_gate_uam = pulp.LpVariable('gate_uam', lowBound=0, upBound=self.max_gate_uam, cat='Integer')
        self.x_path_out_uam = pulp.LpVariable('path_out_uam', lowBound=0, upBound=self.max_path_out_uam, cat='Integer')
        self.x_fato_out_uam = pulp.LpVariable('fato_out_uam', lowBound=0, upBound=self.max_fato_uam, cat='Integer')
        self.x_gate_uam_psg = pulp.LpVariable('gate_uam_psg', lowBound=0, upBound=4 * self.max_gate_uam, cat='Integer')
        self.x_waiting_room_psg = pulp.LpVariable('waiting_room_psg', lowBound=0, upBound=self.max_waiting_room_psg, cat='Integer')

        self.w1, self.w2, self.w3, self.w4, self.w5, self.w6 = (0.04, 0.02, 0.38, 0.31, 0.1, 0.15)
        self.w7, self.w8, self.w9, self.w10 = (0.31, 0.20, 0.2, 0.29)

    def get_congestion(self):
        congest = self.w1 * self.x_fato_in_uam.varValue / self.max_fato_uam \
                  + self.w2 * self.x_path_in_uam.varValue / self.max_path_in_uam \
                  + self.w3 * self.x_gate_uam.varValue / self.max_gate_uam \
                  + self.w4 * self.x_waiting_room_psg.varValue / self.max_waiting_room_psg \
                  + self.w5 * self.x_path_out_uam.varValue / self.max_path_out_uam \
                  + self.w6 * self.x_fato_out_uam.varValue / self.max_fato_uam
        return congest

    def get_utilization(self):
        utilization = self.w7 * self.x_gate_uam.varValue / self.max_gate_uam \
                      + self.w8 * self.x_gate_uam_psg.varValue / (4 * self.max_gate_uam) \
                      + self.w9 * self.x_path_out_uam.varValue / self.max_path_out_uam \
                      + self.w10 * self.x_fato_out_uam.varValue / self.max_fato_uam
        return utilization

    def set_problem(self) -> pulp.LpProblem:
        problem = pulp.LpProblem("UAM_Optimization", pulp.LpMinimize)
        congest = self.w1 * self.x_fato_in_uam / self.max_fato_uam \
                  + self.w2 * self.x_path_in_uam / self.max_path_in_uam \
                  + self.w3 * self.x_gate_uam / self.max_gate_uam \
                  + self.w4 * self.x_waiting_room_psg / self.max_waiting_room_psg \
                  + self.w5 * self.x_path_out_uam / self.max_path_out_uam \
                  + self.w6 * self.x_fato_out_uam / self.max_fato_uam
        utilization = self.w7 * self.x_gate_uam / self.max_gate_uam \
                      + self.w8 * self.x_gate_uam_psg / (4 * self.max_gate_uam) \
                      + self.w9 * self.x_path_out_uam / self.max_path_out_uam \
                      + self.w10 * self.x_fato_out_uam / self.max_fato_uam
        problem += (congest - self.weight * utilization)

        # 전체 UAM 대수 동일
        problem += self.x_fato_in_uam + self.x_path_in_uam + self.x_gate_uam + self.x_path_out_uam + self.x_fato_out_uam \
                   == self.current_fato_in_uam + self.current_path_in_uam + self.current_gate_uam + self.current_path_out_uam + self.current_fato_out_uam

        # 전체 인원 동일
        problem += 4 * (self.x_path_out_uam + self.x_fato_out_uam) + self.x_gate_uam_psg + self.x_waiting_room_psg \
                   == 4 * (self.current_path_out_uam + self.current_fato_out_uam) + self.current_gate_uam_psg + self.current_waiting_room_psg

        # 대합실 인원은 같거나 줄어듦
        problem += self.x_waiting_room_psg <= self.current_waiting_room_psg

        # 현재 탑승 중인 사람은 4명 채워져서 출발하거나 그대로 대기
        problem += (self.x_path_out_uam + self.x_fato_out_uam) * 4 + self.x_gate_uam_psg >= self.current_gate_uam_psg

        # fato_in + path_in의 UAM 대수는 같거나 줄어듦
        problem += self.x_fato_in_uam + self.x_path_in_uam <= self.current_fato_in_uam + self.current_path_in_uam

        # path_out + fato_out의 UAM 대수는 같거나 늘어남
        problem += self.x_path_out_uam + self.x_fato_out_uam >= self.current_path_out_uam + self.current_fato_out_uam

        # fato_in의 UAM 대수는 같거나 줄어들고 fato_out의 UAM 대수는 같거나 늘어남
        problem += self.x_fato_in_uam <= self.current_fato_in_uam
        problem += self.x_fato_out_uam >= self.current_fato_out_uam
        problem += self.x_fato_in_uam + self.x_fato_out_uam <= self.max_fato_uam

        # gate의 UAM 탑승 인원은 최대 탑승 가능 인원보다 작거나 같음
        problem += self.x_gate_uam_psg <= self.x_gate_uam * 4

        return problem

    def solve(self):
        problem = self.set_problem()
        problem.solve()

        solution = {}
        for var in problem.variables():
            solution[var.name] = var.varValue
        solution['congestion'] = self.get_congestion()
        solution['utilization'] = self.get_utilization()

        return solution
