"""Testes dos calculos puros de patrimonio, metas e rebalanceamento."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "backend"))

from app.modules.portfolios.calculos import (  # noqa: E402
    CalculosCarteira, PosicaoParaRebalanceamento,
)


class TestCalculosCarteira(unittest.TestCase):
    """Exercita formulas com centavos e arredondamento de metas."""

    def test_valor_patrimonio_e_participacao_com_centavos(self):
        valor = CalculosCarteira.valor_posicao(3, Decimal("10.17"))
        total = CalculosCarteira.patrimonio_total([valor, Decimal("0.29")])

        self.assertEqual(valor, Decimal("30.51"))
        self.assertEqual(total, Decimal("30.80"))
        self.assertEqual(CalculosCarteira.participacao(valor, total), Decimal("99.06"))
        self.assertEqual(CalculosCarteira.participacao(Decimal(0), Decimal(0)), Decimal("0.00"))

    def test_novo_ativo_de_13_por_cento_preserva_proporcao_antiga(self):
        metas = {"A": Decimal("50"), "B": Decimal("25"), "C": Decimal("25")}

        resultado = CalculosCarteira.redistribuir_objetivos(metas, "D", Decimal("13"))

        self.assertEqual(resultado, {
            "A": Decimal("43.50"), "B": Decimal("21.75"),
            "C": Decimal("21.75"), "D": Decimal("13.00"),
        })
        self.assertEqual(sum(resultado.values()), Decimal("100.00"))
        self.assertEqual(metas["A"], Decimal("50"))

    def test_redistribuicao_quebrada_fecha_exatamente_cem_por_cento(self):
        metas = {"A": Decimal("33.33"), "B": Decimal("33.33"), "C": Decimal("33.34")}

        resultado = CalculosCarteira.redistribuir_objetivos(metas, "D", Decimal("13.00"))

        self.assertEqual([resultado[t] for t in ("A", "B", "C", "D")], [
            Decimal("29.00"), Decimal("29.00"), Decimal("29.00"), Decimal("13.00"),
        ])
        self.assertEqual(sum(resultado.values()), Decimal("100.00"))

    def test_nova_meta_quebrada_distribui_os_centesimos_restantes(self):
        resultado = CalculosCarteira.redistribuir_objetivos(
            {"A": Decimal("50"), "B": Decimal("25"), "C": Decimal("25")},
            "D", Decimal("13.37"),
        )

        self.assertEqual(resultado, {
            "A": Decimal("43.31"), "B": Decimal("21.66"),
            "C": Decimal("21.66"), "D": Decimal("13.37"),
        })
        self.assertEqual(sum(resultado.values()), Decimal("100.00"))

    def test_primeiro_ativo_e_metadados_invalidos(self):
        self.assertEqual(
            CalculosCarteira.redistribuir_objetivos({}, "A", Decimal("100")),
            {"A": Decimal("100.00")},
        )
        with self.assertRaises(ValueError):
            CalculosCarteira.redistribuir_objetivos({}, "A", Decimal("50"))
        with self.assertRaises(ValueError):
            CalculosCarteira.redistribuir_objetivos({"A": Decimal("50")}, "B", Decimal("13"))
        with self.assertRaises(ValueError):
            CalculosCarteira.redistribuir_objetivos({"A": Decimal("100")}, "A", Decimal("13"))

    def test_simulacao_com_precos_quebrados_e_saldo_restante(self):
        posicoes = [
            PosicaoParaRebalanceamento("A", 0, Decimal("1.23"), Decimal("50")),
            PosicaoParaRebalanceamento("B", 0, Decimal("0.61"), Decimal("25")),
            PosicaoParaRebalanceamento("C", 0, Decimal("0.61"), Decimal("25")),
        ]

        # A parcela de A (122,685) nao cobre seu lote de 123; a sobra nao migra.
        resultado = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("245.37"), "linear")

        self.assertEqual(resultado.valor_investido, Decimal("122.00"))
        self.assertEqual(resultado.saldo_restante, Decimal("123.37"))
        self.assertEqual(resultado.patrimonio_projetado, Decimal("122.00"))
        self.assertEqual([a.quantidade_sugerida for a in resultado.ativos], [0, 100, 100])
        self.assertEqual([a.participacao_projetada for a in resultado.ativos], [
            Decimal("0.00"), Decimal("50.00"), Decimal("50.00"),
        ])
        self.assertEqual([a.distancia_projetada for a in resultado.ativos], [
            Decimal("-50.00"), Decimal("25.00"), Decimal("25.00"),
        ])
        self.assertEqual([p.quantidade for p in posicoes], [0, 0, 0])

    def test_ativo_novo_recebe_aporte_sem_comprar_os_acima_da_meta(self):
        metas = CalculosCarteira.redistribuir_objetivos(
            {"A": Decimal("50"), "B": Decimal("25"), "C": Decimal("25")},
            "NOVO", Decimal("13"),
        )
        posicoes = [
            PosicaoParaRebalanceamento("A", 100, Decimal("50.00"), metas["A"]),
            PosicaoParaRebalanceamento("B", 100, Decimal("25.00"), metas["B"]),
            PosicaoParaRebalanceamento("C", 100, Decimal("25.00"), metas["C"]),
            PosicaoParaRebalanceamento("NOVO", 0, Decimal("1.33"), metas["NOVO"]),
        ]

        resultado = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("1000.00"))

        self.assertEqual([a.quantidade_sugerida for a in resultado.ativos], [0, 0, 0, 700])
        self.assertEqual(resultado.valor_investido, Decimal("931.00"))
        self.assertEqual(resultado.saldo_restante, Decimal("69.00"))
        self.assertEqual(resultado.ativos[-1].distancia_atual, Decimal("-13.00"))
        self.assertLess(resultado.ativos[-1].distancia_projetada, Decimal(0))

    def test_distancias_indicam_excesso_falta_e_meta_atingida(self):
        """Distancia positiva indica excesso; negativa indica falta na meta."""
        posicoes = [
            PosicaoParaRebalanceamento("A", 100, Decimal("10.00"), Decimal("50")),
            PosicaoParaRebalanceamento("B", 0, Decimal("10.00"), Decimal("50")),
        ]

        resultado = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("1000.00"))

        self.assertEqual([a.distancia_atual for a in resultado.ativos], [
            Decimal("50.00"), Decimal("-50.00"),
        ])
        self.assertEqual([a.distancia_projetada for a in resultado.ativos], [
            Decimal("0.00"), Decimal("0.00"),
        ])
        self.assertEqual([a.quantidade_sugerida for a in resultado.ativos], [0, 100])

    def test_lote_inviavel_deixa_aporte_intacto(self):
        posicoes = [PosicaoParaRebalanceamento("A", 0, Decimal("1.01"), Decimal("100"))]

        resultado = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("100.99"))

        self.assertEqual(resultado.valor_investido, Decimal("0.00"))
        self.assertEqual(resultado.saldo_restante, Decimal("100.99"))
        self.assertEqual(resultado.ativos[0].quantidade_sugerida, 0)

    def test_minimo_considera_divisao_e_limite_exato_do_lote(self):
        """Um lote barato pode exigir aporte maior pela parcela destinada ao ativo."""
        posicoes = [
            PosicaoParaRebalanceamento("A", 200, Decimal("10"), Decimal("40")),
            PosicaoParaRebalanceamento("B", 600, Decimal("10"), Decimal("30")),
            PosicaoParaRebalanceamento("C", 200, Decimal("10"), Decimal("30")),
        ]
        referencia = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal(0))
        self.assertEqual(referencia.aporte_minimo, Decimal("1500.00"))
        self.assertEqual([a.aporte_minimo_ativo for a in referencia.ativos], [Decimal("1500"), None, Decimal("3000")])
        self.assertTrue(all(a.custo_lote == Decimal("1000.00") for a in referencia.ativos))
        abaixo = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("1499.99"))
        self.assertEqual(abaixo.valor_investido, 0)
        minimo = CalculosCarteira.simular_rebalanceamento(posicoes, referencia.aporte_minimo)
        self.assertEqual(minimo.ativos[0].quantidade_sugerida, 100)

    def test_minimo_linear_arredonda_centavo_para_cima(self):
        """A referencia nao promete um lote quando falta uma fracao de centavo."""
        posicoes = [PosicaoParaRebalanceamento("A", 700, Decimal(10), Decimal(70)),
                    PosicaoParaRebalanceamento("B", 300, Decimal(10), Decimal(30))]
        self.assertIsNone(CalculosCarteira.simular_rebalanceamento(posicoes, Decimal(0)).aporte_minimo)
        referencia = CalculosCarteira.simular_rebalanceamento(posicoes, Decimal(0), "linear")
        self.assertEqual(referencia.aporte_minimo, Decimal("1428.58"))
        self.assertEqual(CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("1428.57"), "linear").valor_investido, 0)
        self.assertEqual(CalculosCarteira.simular_rebalanceamento(posicoes, Decimal("1428.58"), "linear").ativos[0].quantidade_sugerida, 100)

    def test_rejeita_meta_incompleta_e_cotacao_invalida(self):
        with self.assertRaises(ValueError):
            CalculosCarteira.simular_rebalanceamento(
                [PosicaoParaRebalanceamento("A", 0, Decimal("1.00"), Decimal("99.99"))],
                Decimal("100.00"),
            )
        with self.assertRaises(ValueError):
            CalculosCarteira.simular_rebalanceamento(
                [PosicaoParaRebalanceamento("A", 0, Decimal("0.00"), Decimal("100"))],
                Decimal("100.00"),
            )


if __name__ == "__main__":
    unittest.main()
