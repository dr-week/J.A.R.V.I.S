import unittest
from backend.app.hands.registry import REGISTRY, _EXECUTORS
import tools.money_maker  # Triggers auto-registration

class TestMoneyMakerPlugin(unittest.TestCase):
    def test_money_maker_tools_registered(self):
        """Verify all Money Maker tools are registered in Jarvis hands registry."""
        self.assertIn("mm_scan_market", REGISTRY)
        self.assertIn("mm_draft_outreach", REGISTRY)
        self.assertIn("mm_scan_freebies_and_deals", REGISTRY)
        self.assertIn("mm_calculate_expected_value", REGISTRY)
        self.assertIn("mm_detect_arbitrage_spread", REGISTRY)
        self.assertIn("mm_valuate_asset", REGISTRY)
        self.assertIn("mm_track_expenses", REGISTRY)
        self.assertIn("mm_monte_carlo_sim", REGISTRY)
        self.assertIn("mm_set_financial_goal", REGISTRY)
        self.assertIn("mm_track_assumption", REGISTRY)
        self.assertIn("mm_analyze_sentiment", REGISTRY)

    def test_asset_valuation(self):
        """Verify fundamental valuation ratios calculation."""
        executor = _EXECUTORS.get("mm_valuate_asset")
        self.assertIsNotNone(executor)
        
        # Current Price 4000 / EPS 250 = PE 16.0 (Sector average 25.0 -> < 18.75 is UNDERVALUED)
        res = executor(ticker="TCS", current_price=4000, earnings_per_share=250, sector_average_pe=25.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["pe_ratio"], 16.0)
        self.assertIn("UNDERVALUED", res["valuation_status"])

    def test_expense_tracking(self):
        """Verify transaction categorization and budget limit calculations."""
        executor = _EXECUTORS.get("mm_track_expenses")
        self.assertIsNotNone(executor)
        
        txs = [
            {"description": "Freelance Payout", "amount": 100000, "category": "Income"},
            {"description": "Server Hosting", "amount": -5000, "category": "Infra"},
            {"description": "Groceries", "amount": -15000, "category": "Food"}
        ]
        res = executor(transactions=txs, monthly_budget_inr=50000)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_spent"], 20000.0)
        self.assertEqual(res["net_savings"], 80000.0)
        self.assertFalse(res["is_overbudget"])

    def test_monte_carlo_simulation(self):
        """Verify Monte Carlo simulation returns valid distribution."""
        executor = _EXECUTORS.get("mm_monte_carlo_sim")
        self.assertIsNotNone(executor)
        
        res = executor(initial_capital=50000, win_probability=0.6, win_payout_multiplier=2.0, num_simulations=100)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["profit_probability_pct"], 50.0)

    def test_goal_engine(self):
        """Verify setting financial goal and real-time assumptions."""
        goal_exec = _EXECUTORS.get("mm_set_financial_goal")
        assump_exec = _EXECUTORS.get("mm_track_assumption")
        self.assertIsNotNone(goal_exec)
        self.assertIsNotNone(assump_exec)
        
        g_res = goal_exec(goal_name="Q3 MRR Target", target_amount_inr=300000, strategy_archetype="Micro-SaaS Kits", deadline_days=30)
        self.assertEqual(g_res["status"], "success")
        self.assertEqual(g_res["goal_details"]["daily_target_inr"], 10000.0)
        
        a_res = assump_exec(hypothesis_key="UPI_BOOM", assumption_statement="UPI transactions will grow 20%", confidence_score=0.85, invalidation_condition="RBI regulation changes")
        self.assertEqual(a_res["status"], "success")
        self.assertTrue(a_res["is_valid"])

    def test_sentiment_analysis(self):
        """Verify Fear & Greed sentiment calculation."""
        executor = _EXECUTORS.get("mm_analyze_sentiment")
        self.assertIsNotNone(executor)
        
        bullish_news = ["Tech stocks surge to record high", "Startup posts record growth and profit"]
        res = executor(headlines=bullish_news)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["sentiment_score"], 100.0)
        self.assertIn("GREED", res["sentiment_label"])

    def test_expected_value_calculation(self):
        """Verify Expected Value math and favorable edge detection."""
        executor = _EXECUTORS.get("mm_calculate_expected_value")
        self.assertIsNotNone(executor)
        
        # 60% chance to win ₹10,000 vs 40% chance to lose ₹2,000 -> EV = +₹5,200
        res = executor(win_probability=0.6, potential_gain=10000, loss_probability=0.4, potential_loss=2000)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["expected_value"], 5200.0)
        self.assertTrue(res["is_favorable"])

    def test_arbitrage_spread_detection(self):
        """Verify real net arbitrage calculation after fees."""
        executor = _EXECUTORS.get("mm_detect_arbitrage_spread")
        self.assertIsNotNone(executor)
        
        res = executor(
            asset_name="BTC",
            price_exchange_a=60000,
            exchange_a_name="Exchange A",
            price_exchange_b=61500,
            exchange_b_name="Exchange B",
            fee_percentage=0.2
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_opportunity"])
        self.assertGreater(res["net_profit_per_unit"], 1000.0)

    def test_money_maker_risk_levels(self):
        """Verify safety risk gates are strictly enforced."""
        # Market scanner is read-only -> auto
        self.assertEqual(REGISTRY["mm_scan_market"]["risk_level"], "auto")
        
        # Deals scanner is read-only -> auto
        self.assertEqual(REGISTRY["mm_scan_freebies_and_deals"]["risk_level"], "auto")
        
        # Communication / Outreach MUST be confirm_always
        self.assertEqual(REGISTRY["mm_draft_outreach"]["risk_level"], "confirm_always")

    def test_draft_outreach_execution(self):
        """Test drafting outreach messages."""
        executor = _EXECUTORS.get("mm_draft_outreach")
        self.assertIsNotNone(executor)
        
        result = executor(target_name="Acme Corp", objective="AI Automation Consulting")
        self.assertEqual(result["status"], "success")
        self.assertIn("Acme Corp", result["action_taken"])
        self.assertIn("AI Automation Consulting", result["draft_content"])

    def test_freebies_scanner_structure(self):
        """Verify the freebies and deals scanner output schema."""
        executor = _EXECUTORS.get("mm_scan_freebies_and_deals")
        self.assertIsNotNone(executor)
        
        report = executor()
        self.assertIn("scan_time", report)
        self.assertIn("total_found", report)
        self.assertIn("top_picks", report)
        self.assertIn("categorized", report)
        self.assertIsInstance(report["top_picks"], list)

if __name__ == "__main__":
    unittest.main()
