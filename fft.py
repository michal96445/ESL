from myhdl import *
from math import cos, pi
import pylab
import os


def unit_singen(i_clk, i_reset, i_enable, o_outvalue, frequenzSIN, clkfrequnez):
    INTERNALWIDTH = len(o_outvalue) - 2
    KONSTANT_FACTOR = int(cos(2 * pi * frequenzSIN * 1.0 / clkfrequnez) * 2 ** (INTERNALWIDTH))

    Reg_T0 = Signal(intbv((2 ** (INTERNALWIDTH)) - 1, min=o_outvalue.min, max=o_outvalue.max))
    Reg_T1 = Signal(intbv(KONSTANT_FACTOR, min=o_outvalue.min, max=o_outvalue.max))

    @always(i_clk.posedge, i_reset.negedge)
    def logicCC():
        if i_reset == 0:
            Reg_T0.next = (2 ** (INTERNALWIDTH)) - 1
            Reg_T1.next = KONSTANT_FACTOR
        else:
            if i_enable == 1:
                Reg_T0.next = Reg_T1
                Reg_T1.next = ((KONSTANT_FACTOR * Reg_T1) >> (INTERNALWIDTH - 1)) - Reg_T0

    @always_comb
    def comb_logic():
        o_outvalue.next = Reg_T1

    return instances()


def test_singen(SimulateNPoints=20):
    OUTPUT_BITWIDTH = 50
    output = Signal(intbv(0, min=-2 * OUTPUT_BITWIDTH, max=2 * OUTPUT_BITWIDTH))
    clk = Signal(bool(0))
    enable = Signal(bool(0))
    reset = Signal(bool(0))
    frequenzSIN = 3  # make a 3.00 hz Sinus
    clk_frequnez = 100  # 10 mhz
    clk_period = 1.0 / clk_frequnez
    singen_instance = unit_singen(clk, reset, enable, output, frequenzSIN, clk_frequnez)

    @always(delay(int(clk_period * 0.5 * 1e9)))
    def clkgen():
        clk.next = not clk

    out_values = []

    @instance
    def stimulus():
        while 1:
            reset.next = 0
            enable.next = 0
            yield clk.posedge
            reset.next = 1
            yield clk.posedge
            enable.next = 1
            for i in range(SimulateNPoints):
                yield clk.posedge
                out_values.append(int(output))
                print(output)

            pylab.figure(1)
            pylab.plot(pylab.arange(0.0, clk_period * (len(out_values) - 0.5), clk_period), out_values)
            pylab.xlabel("Time")
            pylab.ylabel("Amplitude")
            pylab.show()
            raise StopSimulation

    toVHDL(unit_singen, clk, reset, enable, output, frequenzSIN, clk_frequnez)

    return instances()


if __name__ == '__main__':
    trace_save_path = '../out/testbench/'
    vhdl_output_path = '../out/vhdl/'
    os.makedirs(os.path.dirname(trace_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(vhdl_output_path), exist_ok=True)

    sim = Simulation(test_singen(SimulateNPoints=200))
    sim.run()
    