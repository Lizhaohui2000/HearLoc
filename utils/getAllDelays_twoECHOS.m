function tau_arr = getAllDelays_twoECHOS(P_s, P_2, P_1, Fs, c)
    if nargin<=3
        Fs = 48000;
    end
    if nargin<=4
        c = 343;
    end
    
    P_1v_1 = -P_1; P_1v_1(2) = P_1v_1(2);
    P_1v_2 = -P_1; P_1v_2(2) = P_1v_2(2);

    P_2v_1 = P_2; P_2v_1(2) = -P_2v_1(2); 
    P_2v_2 = P_2; P_2v_2(2) = -P_2v_2(2); 

    tau_arr = [getTau(P_s, P_2, P_1); getTau(P_s, P_2v_1, P_1v_1); getTau(P_s, P_2v_1, P_1); getTau(P_s, P_2, P_1v_1); 
        getTau(P_s, P_2v_2, P_1v_2); getTau(P_s, P_2v_2, P_1); getTau(P_s, P_2, P_1v_2); getTau(P_s, P_2v_2, P_1v_1); getTau(P_s, P_2v_1, P_1v_2); ]*Fs;

    function ret = getTau(P_s, P_2, P_1)
        ret = (norm((P_s-P_2))-norm((P_s-P_1)))/c;
    end

end