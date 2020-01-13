--[[    lua script : xss_sqli_body.lua
	purpose    : to check the url is matched in Potential XSS and SQLi Attacks (Body) or not
	rule       : reject tcp any any -> any any (msg:"Potentail XSS and SQLi Attacks (Body)"; luajit:xss_sqli_body.lua; priority:1; sid: 100000000000; rev:1;)

	author     : samiux (https://www.infosec-ninjas.com)
	project    : Croissants
	license    : GPLv3
	date       : SEP 24, 2018

	Remarks    : (1) https protocol will not be processed.
		     (2) google safe-browsing blacklisted is also not processed
		         as it is blocked by firefox before suricata processing.
]]

-- this gets called during rule parsing
function init(args)
	local needs = {}
 	needs["http.request_body"] = tostring(true)
	return needs
end

-- this is a matcher function
function match(args)
	-- initalization
	-- verbose = 0 (false), 1 (true, default)
	local verbose = 0

	-- get request body
	http_body = string.lower(tostring(HttpGetRequestBody()))

	if http_body == nil then
		http_body = ""
	end

	-- open files
  	local url_file = io.open("/etc/suricata/rules/xss_sqli_pattern.url", "r")
	local access_file = io.open("/var/log/suricata/xss.log", "a")

	-- compare request body
	for line in url_file:lines() do
		if #http_body > 0 then
			if string.find(line, http_body) then
				access_file:write(os.date("[%x - %X] [**]" .. " [Match] " .. http_body .. " <@> Source : " .. line .. " \n"))
				url_file:flush()
				access_file:flush()
				url_file:close()
				access_file:close()
				return 1
			else
				if verbose == 1 then
					access_file:write(os.date("[%x - %X] [--] " .. http_body .. " <@> Source : " .. line .. " \n"))
				end
			end
		end
	end
	url_file:flush()
	access_file:flush()
	url_file:close()
	access_file:close()
	return 0
end	

function deinit(args)
        url_file:flush()
        access_file:flush()
        url_file:close()
        access_file:close()
end

