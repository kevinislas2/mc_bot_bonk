-- CONFIGURATION
local URL = "wss://64da4ce18aa1.ngrok-free.app/ws" -- CHANGE THIS!

print("Connecting to bridge...")
local ws, err = http.websocket(URL)

if not ws then
    printError("Connection failed: " .. tostring(err))
    return
end

print("Connected! Chat bridging is active.")

-- 1. Listen for Discord messages -> Print to Game
local function discordListener()
    while true do
        local message = ws.receive() -- Blocks until message arrives
        if message then
            -- Print to terminal with color
            term.setTextColor(colors.cyan)
            print(message)
            term.setTextColor(colors.white)
            
            -- If you have a monitor connected:
            local mon = peripheral.find("monitor")
            if mon then 
               mon.write(message) 
               mon.setCursorPos(1, select(2, mon.getCursorPos()) + 1)
            end
        else
            print("WebSocket closed.")
            break
        end
    end
end

-- 2. Listen for Minecraft Chat -> Send to Discord
local function minecraftListener()
    while true do
        -- The event is slightly different for the peripheral
        -- It returns: event, username, message, uuid, hidden
        local event, username, message, uuid = os.pullEvent("chat")
        
        -- Filter out the bot itself to prevent infinite loops!
        if username ~= "YourMinecraftName" and username ~= "Server" then
             print("Heard: " .. username)
             ws.send(username .. ": " .. message)
        end
    end
end

-- Run both functions in parallel threads
parallel.waitForAny(discordListener, minecraftListener)
ws.close()