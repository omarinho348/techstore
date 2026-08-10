import * as voiceApi from "../api/voiceApi";

export async function transcribeVoice(audioBlob, sessionId) {
    return voiceApi.transcribeVoice(audioBlob, sessionId);
}
