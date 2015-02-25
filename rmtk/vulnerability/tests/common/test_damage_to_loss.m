clc
clear all
close all

function [ LR ] = damage_to_loss( SaT, bTSa, samp, iml )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
cons = dlmread('inputs/consequence.tcl');
for x=1:length(iml)
for i=1:length(SaT)
if bTSa{i}(samp)==0
if iml(x)<exp(SaT{i}(samp)); poe(i)=0; else poe(i) = 1; end
else
poe(i) = logncdf(iml(x),SaT{i}(samp),bTSa{i}(samp));
end
end

poo = poe;
for i=1:length(SaT)-1
poo(i) = poe(i)-poe(i+1);
lr(i) = poo(i)*cons(i);
end

LR(x) = sum(lr)+poo(length(SaT))*cons(length(SaT));
end

end

addpath('./functions/');
Sa = {[0.0969], [0.1452], [0.1626], [0.177], [0.1779]};
b = {[0.1908],[0.3037],[0.3527],[0.3727],[0.3738]};
iml = 0.01:0.01:1;
LR = damage_to_loss(Sa, b, 1, iml);
plot(iml,LR)
