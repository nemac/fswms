CREATE OR REPLACE FUNCTION CreatePestProxAgents()
RETURNS void AS
$BODY$
DECLARE
  --pid pestproxshapes%rowtype;
  pid record;
  in_pid pestproxdata%rowtype; 
  agents varchar(10000);
BEGIN
  FOR pid IN SELECT DISTINCT pt_id FROM pestproxdata ORDER BY pt_id
  LOOP
    agents := '';
    RAISE NOTICE '%', pid.pt_id;
    FOR in_pid IN SELECT * FROM pestproxdata WHERE pt_id=pid.pt_id ORDER BY prob DESC
    LOOP
	RAISE NOTICE '%', in_pid.agent;
	agents := agents || coalesce(upper(in_pid.agent) || ' | Closest Agent (km): ' || round(in_pid.metric1,2) || ' | Acres: ' || round(in_pid.metric2, 2) || ' | Host: ' || in_pid.host || ' | Count: ' || in_pid.count || ' | Yr: ' || in_pid.year || ' | Prob: ' || round(in_pid.prob,2), 'no agents reported within 75km') || E'\n';
    END LOOP;
    --insert into pestproxdataagents
    IF in_pid.agent IS NOT NULL THEN  
       INSERT INTO pestproxdataagents(pt_id,agent_list) VALUES (pid.pt_id,agents); 
       RAISE NOTICE '%', agents;
    END IF;  
  END LOOP;
  RETURN;
END;
$BODY$
LANGUAGE plpgsql;