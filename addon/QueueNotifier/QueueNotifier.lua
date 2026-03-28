QueueNotifierDB = QueueNotifierDB or {}

local frame = CreateFrame("Frame")
frame:RegisterEvent("PVPQUEUE_ANYWHERE_SHOW")
frame:RegisterEvent("PVPQUEUE_ANYWHERE_HIDE")
frame:RegisterEvent("PLAYER_LOGIN")

frame:SetScript("OnEvent", function(self, event)
    if event == "PLAYER_LOGIN" then
        print("|cff00ccff[QueueNotifier]|r Loaded. Waiting for queue pop...")

    elseif event == "PVPQUEUE_ANYWHERE_SHOW" then
        QueueNotifierDB.lastPop = time()
        QueueNotifierDB.status = "popped"
        print("|cff00ff00[QueueNotifier]|r Queue popped! Notification sent.")

    elseif event == "PVPQUEUE_ANYWHERE_HIDE" then
        QueueNotifierDB.status = "closed"
    end
end)
