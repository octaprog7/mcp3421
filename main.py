import sys
from machine import I2C, Pin
from sensor_pack_2.bus_service import I2cAdapter
import mcp3421mod
import time


def get_input_leg_names(in_mux_config: int) -> tuple[str, str]:
    """возвращает кортеж имен входных выводов микросхемы"""
    if 0 == in_mux_config:
        return "AIN0", "AIN1"
    if 1 == in_mux_config:
        return "AIN0", "AIN3"
    if 2 == in_mux_config:
        return "AIN1", "AIN3"
    if 3 == in_mux_config:
        return "AIN2", "AIN3"
    if 4 == in_mux_config:
        return "AIN0", "GND"
    if 5 == in_mux_config:
        return "AIN1", "GND"
    if 6 == in_mux_config:
        return "AIN2", "GND"
    if 7 == in_mux_config:
        return "AIN3", "GND"


def get_full_scale_range(gain_amp: int) -> float:
    """возвращает диапазон полной шкалы в Вольтах"""
    _fsr = 6.144, 4.096, 2.048, 1.024, 0.512, 0.256
    return _fsr[gain_amp]


'''
def decode_common_props(source: ads1115mod.common_props):
    """Выводит в stdout основные свойства АЦП"""
    if not source.operational_status:
        print("operational status: устройство выполняет преобразование")
    else:
        print("operational status: устройство не выполняет преобразование")
    legs = get_input_leg_names(source.in_mux_config)
    print(f"in mux config: positive leg: {legs[0]}; negative leg: {legs[1]}")
    print(f"gain amplifier +/-: {get_full_scale_range(source.gain_amplifier)} [Вольт]")
    if not source.operating_mode:
        print("operating mode: режим непрерывного преобразования")
    else:
        print("operating mode: режим одиночного преобразования или состояние отключения питания")
    if source.data_rate < 5:
        print(f"data rate: {8 * 2 ** source.data_rate} отсчетов в секунду(!)")
    else:
        tmp = 250, 475, 860
        print(f"data rate: {tmp[source.data_rate - 5]} отсчетов в секунду(!)")
'''

if __name__ == '__main__':
    i2c = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=400_000)  # on Raspberry Pi Pico
    adapter = I2cAdapter(i2c)

    adc = mcp3421mod.Mcp3421(adapter)
    # print(adc)
    # b = adc.read(4)
    # print(b)
    #    adc.start_measurement(single_shot=True, data_rate_raw=0, gain_raw=0, channel=0, differential_channel=True)
    #    wt = adc.get_conversion_cycle_time()
    #    print(f"Время преобразования: {wt} мкс")
    #    time.sleep_us(wt)
    #    val = adc.get_value(raw=True)
    #    print(f"Напряжение: {val} Вольт")

    print("---Одиночный режим измерения---")
    my_gain = 0
    my_data_rate = 2
    adc.start_measurement(single_shot=True, data_rate_raw=my_data_rate, gain_raw=my_gain,
                          channel=0, differential_channel=True)
    print("---Основные 'сырые' настройки датчика---")
    gp = adc.get_general_raw_props()
    print(gp)
    print(16 * "--")
    td = adc.get_conversion_cycle_time()
    print(f"Время преобразования [мкс]: {td}")
    print(f"Бит в отсчете: {adc.current_resolution}")
    print(f"PGA: {adc.gain}")
    print(16 * "--")
    for _ in range(33):
        time.sleep_us(td)
        # print(f"value: {adc.value}; raw: {adc.get_value(raw=True)}")
        val = adc.get_value(raw=False)
        # lsb = adc.get_lsb()
        # print(f"value: {val};\tLSB [Вольт]: {lsb}")
        # val = adc.get_raw_value_ex()
        print(val)
        adc.start_measurement(single_shot=True, data_rate_raw=my_data_rate, gain_raw=my_gain,
                              channel=0, differential_channel=True)

    print(16 * "--")
    print("Автоматический режим измерений АЦП")
    print(16 * "--")
    adc.start_measurement(single_shot=False, data_rate_raw=my_data_rate, gain_raw=my_gain,
                          channel=0, differential_channel=True)
    td = adc.get_conversion_cycle_time()
    time.sleep_us(td)
    print(f"Время преобразования [мкс]: {td}")
    print(f"Бит в отсчете: {adc.current_resolution}")
    _cnt, _max = 0, 333333
    for voltage in adc:
        print(f"Напряжение: {voltage} Вольт")
        if _cnt > _max:
            sys.exit(0)
        time.sleep_us(td)
        _cnt += 1
