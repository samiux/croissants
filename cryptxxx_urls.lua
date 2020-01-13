--[[    lua script : cryptxxx_urls.lua
	purpose    : to check the url is matched in blacklisted CryptXXX Ransomware or not
	rule       : reject tcp any any -> any any (msg:"CryptXXX Ransomware blacklisted URL"; luajit:cryptxxx_urls.lua; priority:1; sid: 100000000000; rev:1;)

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
 	needs["http.request_headers"] = tostring(true)
	return needs
end

-- this is a matcher function
function match(args)
	-- initalization
	-- verbose = 0 (false), 1 (true, default)
	local verbose = 0

	-- get host name
	http_host = HttpGetRequestHost()

	if http_host == nil then
		http_host = ""
	end

	-- open files
  	local url_file = io.open("/etc/suricata/rules/cryptxxx.url", "r")
	local access_file = io.open("/var/log/suricata/cryptxxx_urls.log", "a")

	-- compare host name
	for line in url_file:lines() do
		if #http_host > 0 then
			if string.find(line, http_host) then
				access_file:write(os.date("[%x - %X] [**]" .. " [Match] " .. http_host .. " <@> Source : " .. line .. " \n"))
				url_file:flush()
				access_file:flush()
				url_file:close()
				access_file:close()
				return 1
			else
				if verbose == 1 then
					access_file:write(os.date("[%x - %X] [--] " .. http_host .. " <@> Source : " .. line .. " \n"))
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
