clear; 
Fs = 48000;
d_a = 0.05;
c = 343;
minterp = 9;
M = 4;
D = (M-1)*d_a;
d_w_max = 0.8;
mrange = round(2*d_w_max/c*Fs+D/c*Fs+20);

rootname = '.\arrayCalibration\';

%%%% load file
filename = 'sound_4_0.3.txt'; %   a_50_3_8_s_69_24_8
pattern = '(\d+)\.txt$';
matches = regexp(filename, pattern, 'tokens');
P_s_GT = [0, str2double(matches{1}{1})]/10;
y_arr = load([rootname, filename]);
    
%%%% get CC spectrum
R_arr = [];
for k = 1:(size(y_arr, 2)-1)
    for l = (k+1):size(y_arr, 2)
        [~, R] = my_gccphat(y_arr(:,l), y_arr(:,k)); %  len(R)=2*len(y)+1
        length(R)
        R = R((length(y_arr)+(-mrange:mrange)+1),:);
        R = interp1((-mrange:mrange), R, (-mrange:(1/minterp):mrange)');
        R_arr = [R_arr, R];
    end
end

d_w = 0:0.01:0.8;
theta = (0:(360-1))/180*pi;
LSE_arr = zeros(length(d_w_max), length(theta));
for m = 1:length(d_w)
    for n = 1:length(theta)
        LSE_arr(m,n) = computeSum(R_arr, [d_w(m), theta(n)]);
    end
end
imagesc(theta, d_w, -LSE_arr)

% res = fmincon(@(x) computeSum(R_arr, x), [0,0], [],[],[],[], [0, 0], [0.8, 2*pi]);
function LSE_arr = computeSum(R_arr, x)
    Fs = 48000;
    c = 343;
    d_w = x(1);
    theta = x(2);
    d_w_max = 0.8; 
    d_a = 0.05;
    M = 4;
    D = (M-1)*d_a;
    minterp = 9;
    mrange = round(2*d_w_max/c*Fs+D/c*Fs+20);

    P_s = [0, d_w];
    P_a = [3/2*d_a*cos(theta), d_w-3/2*d_a*sin(theta); 1/2*d_a*sin(theta), d_w-1/2*d_a*sin(theta); ...
        1/2*d_a*sin(theta), d_w+1/2*d_a*sin(theta); 3/2*d_a*sin(theta), d_w+3/2*d_a*sin(theta)];
    
    mtag = 1;
    LSE_arr = 0;
    for l = 1:(M-1)
        for k = (l+1):M
            tau_arr = computeDelays(P_s, P_a(k,:), P_a(l,:));
            idx_arr = round((tau_arr+mrange)*minterp+1);
            LSE_arr = LSE_arr + sum(R_arr(idx_arr, mtag));
            mtag = mtag+1;
        end
    end
    
    LSE_arr = -LSE_arr;
    function tau_arr = computeDelays(P_s, P_2, P_1)
        Fs = 48000;
        c = 343;
    
        P_2v = P_2; P_2v(2) = -P_2v(2); 
        P_1v = P_1; P_1v(2) = -P_1v(2);
    
        tau_arr = [getTau(P_s, P_2, P_1); getTau(P_s, P_2v, P_1); getTau(P_s, P_2, P_1v); getTau(P_s, P_2v, P_1v)]*Fs;
    
        function ret = getTau(P_s, P_2, P_1)
            c = 343; 
            ret = (norm((P_s-P_2))-norm((P_s-P_1)))/c;
        end
    end
end
