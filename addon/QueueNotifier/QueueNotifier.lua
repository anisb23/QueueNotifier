QueueNotifierDB = QueueNotifierDB or {}

local frame = CreateFrame("Frame")
frame:RegisterEvent("UPDATE_BATTLEFIELD_STATUS")
frame:RegisterEvent("PLAYER_LOGIN")

frame:SetScript("OnEvent", function(self, event)
    if event == "PLAYER_LOGIN" then
        print("|cff00ccff[QueueNotifier]|r Loaded. Waiting for queue pop...")

    elseif event == "UPDATE_BATTLEFIELD_STATUS" then
        for i = 1, MAX_BATTLEFIELD_QUEUES do
            local status, _, _, _, _, _, _, _, _, _, _, isSoloQueue = GetBattlefieldStatus(i)
            if status == "confirm" and isSoloQueue then
                QueueNotifierDB.lastPop = time()
                QueueNotifierDB.status = "popped"
                print("|cff00ff00[QueueNotifier]|r Solo Shuffle queue popped! Notification sent.")
                break
            end
        end

    end
end)
