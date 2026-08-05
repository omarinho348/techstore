import * as voiceApi from "../api/voiceApi";

export async function sendVoice(
    audioBlob,
    sessionId,
) {
    return await voiceApi.sendVoice(
        audioBlob,
        sessionId,
    );
}