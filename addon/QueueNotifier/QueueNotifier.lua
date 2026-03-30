QueueNotifierDB = QueueNotifierDB or {}

local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_LOGIN")

frame:SetScript("OnEvent", function(self, event)
    if event == "PLAYER_LOGIN" then
        print("|cff00ccff[QueueNotifier]|r Loaded. Waiting for queue pop...")
    end
end)

local function sendNotification()
    local originalFormat = GetCVar("screenshotFormat")
    if originalFormat ~= "tga" then
        SetCVar("screenshotFormat", "tga")
    else
        originalFormat = "jpeg"
    end
    Screenshot()
    SetCVar("screenshotFormat", originalFormat)
end

hooksecurefunc("PVPReadyDialog_Display", function(_, battlefieldId)
    local status, _, _, _, _, queueType = GetBattlefieldStatus(battlefieldId)
    if status == "confirm" and queueType == "RATEDSHUFFLE" then
        print("|cff00ff00[QueueNotifier]|r Solo Shuffle queue popped! Notification sent.")
        sendNotification()
    end
end)
