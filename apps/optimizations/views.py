from rest_framework.views import APIView
from ..vertiports.models import Vertiport
from .utils.vertiportMILP import *
from .utils.getState import getState
from .utils.nextStateSequence import nextStateSequence
from .serializers import *
from rest_framework import status
from rest_framework.response import Response


class OptimizationView(APIView):
    def post(self, request):
        # 필요한 데이터
        json_data = request.data
        user = request.user
        vertiport = Vertiport.objects.get(name=json_data['name'])
        json_state = json_data['state']
        weight = round(json_data['weight'], 2)

        # 최적해 계산
        vertiportMILP = VertiportMILP(vertiport, json_state, weight)
        solution = vertiportMILP.solve()

        # 회원인 경우 결과 저장
        if user.is_authenticated:
            res_state = 'null'
            res_optimization = 'null'

            # 새로운 state이면 저장
            state = getState(json_state, vertiport)
            if not state:
                json_state['sequence'] = nextStateSequence(user, vertiport)
                try:
                    serializer = StateSerializer(data=json_state)
                    if serializer.is_valid():
                        state = serializer.save(user=user, vertiport=vertiport)
                        res_state = str(state)
                except Exception as e:
                    pass

            # 최적해 저장
            try:
                solution['weight'] = round(json_data['weight'], 2)
                serializer = OptimizationSerializer(data=solution)
                if serializer.is_valid():
                    optimization = serializer.save(state=state)
                    res_optimization = str(optimization)
            except Exception as e:
                print(serializer.errors)
                pass

            return Response({'result': 'success', 'data': {'solution': solution, 'state': res_state, 'optimization': res_optimization}}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'success', 'data': {'solution': solution}}, status=status.HTTP_200_OK)
