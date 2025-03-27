from binance.um_futures import UMFutures

from config import instruments
from controller.data_provider import DataProvider
from controller.positions_controller import PositionsController
from controller.technical_analysis import TechnicalAnalysis

data_provider = DataProvider()
technical_analysis = TechnicalAnalysis()
positions_controller = PositionsController()

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = UMFutures(api_key, api_secret)

while True:
    for instrument in instruments:
        historical_1m_data = data_provider.fetch_historical_data(client=client, symbol=instrument['name'],
                                                                 interval='1m')
        applied_1m_df = technical_analysis.calculate_signals(historical_1m_data)
        applied_hl_1m_df = technical_analysis.entry_exit_arrows(historical_1m_data, length=15)

        active_position = positions_controller.get_active_position(instrument['name'])

        if active_position and active_position['direction'] == 1:
            if applied_1m_df.iloc[-1].sell_signal and applied_1m_df.iloc[-1].down_arrow:
                positions_controller.exit_position(active_position, applied_1m_df.iloc[-1].close)
                print(f"Exited LONG for {instrument['name']} at {applied_1m_df.iloc[-1].close}")

        if active_position and active_position['direction'] == 2:
            if applied_1m_df.iloc[-1].buy_signal and applied_1m_df.iloc[-1].up_arrow:
                positions_controller.exit_position(active_position, applied_1m_df.iloc[-1].close)
                print(f"Exited SHORT for {instrument['name']} at {applied_1m_df.iloc[-1].close}")

        active_position = positions_controller.get_active_position(instrument['name'])

        # Check for buy signals
        if applied_1m_df.iloc[-1].buy_signal and applied_1m_df.iloc[-1].up_arrow:
            if active_position and active_position['direction'] != 1:  # Not LONG
                positions_controller.exit_position(active_position, applied_1m_df.iloc[-1].close)
                print(f"Exited opposing SHORT for {instrument['name']} at {applied_1m_df.iloc[-1].close}")

            if not active_position or active_position['direction'] != 1:  # Enter LONG
                print(
                    f"LONG {instrument['name']} at {applied_1m_df.iloc[-1].close} on {applied_1m_df.iloc[-1].open_time}")
                positions_controller.enter_new_position(instrument['name'], applied_1m_df.iloc[-1].close, 1)

        # Check for sell signals
        if applied_1m_df.iloc[-2].sell_signal and applied_1m_df.iloc[-1].down_arrow:
            if active_position and active_position['direction'] != 2:  # Not SHORT
                positions_controller.exit_position(active_position, applied_1m_df.iloc[-1].close)
                print(f"Exited opposing LONG for {instrument['name']} at {applied_1m_df.iloc[-1].close}")

            if not active_position or active_position['direction'] != 2:  # Enter SHORT
                print(
                    f"SHORT {instrument['name']} at {applied_1m_df.iloc[-1].close} on {applied_1m_df.iloc[-1].open_time}")
                positions_controller.enter_new_position(instrument['name'], applied_1m_df.iloc[-1].close, 2)
