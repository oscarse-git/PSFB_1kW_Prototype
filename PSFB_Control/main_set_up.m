close all
clear all

fs = 400e3;

Vin = 100;
MaxPow = 1000;

n_series = 20;
n_parallel = 6;
capacity = 2.16e3; % kWh

Vmax_cell = 4.2; % V
Vmin_cell = 3; % V
capacity_cell = 5; % Ah

Imax = MaxPow/Vmax;



