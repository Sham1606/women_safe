"""Stress detection routes for AI engine integration"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.core.security import device_token_required
import logging
import base64
import tempfile
import os

logger = logging.getLogger(__name__)

stress_bp = Blueprint('stress-detection', __name__)


@stress_bp.route('/analyze-audio', methods=['POST'])
@device_token_required
def analyze_audio():
    """Analyze audio for stress detection
    
    Headers:
        X-Device-Token: Device authentication token
    
    Body:
        audio_base64: Base64 encoded audio file (WAV format)
        heart_rate: Optional current heart rate
        temperature: Optional current temperature
    """
    try:
        device = request.device
        data = request.get_json()
        
        if 'audio_base64' not in data:
            return jsonify({
                'success': False,
                'error': 'audio_base64 is required'
            }), 400
        
        # Decode audio
        try:
            audio_data = base64.b64decode(data['audio_base64'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid base64 encoding'
            }), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_data)
            audio_path = tmp_file.name
        
        try:
            # Import AI engine
            from ai_engine.inference_service import StressInferenceService
            
            # Get inference service
            inference_service = StressInferenceService.get_instance()
            
            # Check if model is loaded
            if not inference_service.is_model_loaded():
                return jsonify({
                    'success': False,
                    'error': 'AI model not loaded. Please train the model first.'
                }), 503
            
            # Analyze audio
            audio_result = inference_service.detect_stress_audio(audio_path)
            
            # Analyze physiological if available
            physiological_result = None
            if 'heart_rate' in data or 'temperature' in data:
                physiological_result = inference_service.analyze_physiological(
                    heart_rate=data.get('heart_rate'),
                    temperature=data.get('temperature')
                )
            
            # Hybrid analysis if both available
            hybrid_result = None
            if physiological_result:
                hybrid_result = inference_service.detect_stress_hybrid(
                    audio_path=audio_path,
                    heart_rate=data.get('heart_rate'),
                    temperature=data.get('temperature')
                )
            
            # Prepare response
            response = {
                'success': True,
                'audio_analysis': audio_result
            }
            
            if physiological_result:
                response['physiological_analysis'] = physiological_result
            
            if hybrid_result:
                response['hybrid_analysis'] = hybrid_result
                response['stress_detected'] = hybrid_result['stress_detected']
                response['combined_score'] = hybrid_result['combined_score']
            else:
                response['stress_detected'] = audio_result['stress_detected']
                response['combined_score'] = audio_result['stress_score']
            
            logger.info(f'Stress analysis completed for device {device.id}: {response["stress_detected"]}')
            
            return jsonify(response), 200
            
        finally:
            # Clean up temp file
            if os.path.exists(audio_path):
                os.remove(audio_path)
        
    except ImportError:
        logger.error('AI engine not available')
        return jsonify({
            'success': False,
            'error': 'AI engine not available. Please install dependencies.'
        }), 503
    except Exception as e:
        logger.error(f'Analyze audio error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to analyze audio',
            'message': str(e)
        }), 500


@stress_bp.route('/analyze-physiological', methods=['POST'])
@device_token_required
def analyze_physiological():
    """Analyze physiological data for stress
    
    Headers:
        X-Device-Token: Device authentication token
    
    Body:
        heart_rate: Heart rate in bpm
        temperature: Temperature in Celsius
    """
    try:
        device = request.device
        data = request.get_json()
        
        heart_rate = data.get('heart_rate')
        temperature = data.get('temperature')
        
        if not heart_rate and not temperature:
            return jsonify({
                'success': False,
                'error': 'At least heart_rate or temperature is required'
            }), 400
        
        try:
            # Import AI engine
            from ai_engine.inference_service import StressInferenceService
            
            # Get inference service
            inference_service = StressInferenceService.get_instance()
            
            # Analyze
            result = inference_service.analyze_physiological(
                heart_rate=heart_rate,
                temperature=temperature
            )
            
            logger.info(f'Physiological analysis for device {device.id}: {result["stress_detected"]}')
            
            return jsonify({
                'success': True,
                **result
            }), 200
            
        except ImportError:
            logger.error('AI engine not available')
            return jsonify({
                'success': False,
                'error': 'AI engine not available'
            }), 503
        
    except Exception as e:
        logger.error(f'Analyze physiological error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to analyze physiological data',
            'message': str(e)
        }), 500


@stress_bp.route('/model-status', methods=['GET'])
@jwt_required()
def get_model_status():
    """Get AI model status"""
    try:
        from ai_engine.inference_service import StressInferenceService
        
        inference_service = StressInferenceService.get_instance()
        is_loaded = inference_service.is_model_loaded()
        
        status = {
            'success': True,
            'model_loaded': is_loaded,
            'model_path': inference_service.model_path if is_loaded else None,
            'scaler_path': inference_service.scaler_path if is_loaded else None
        }
        
        return jsonify(status), 200
        
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'AI engine not available'
        }), 503
    except Exception as e:
        logger.error(f'Get model status error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get model status'
        }), 500


@stress_bp.route('/test', methods=['POST'])
@jwt_required()
def test_stress_detection():
    """Test stress detection with sample data (for development)
    
    Body:
        test_audio_path: Optional path to test audio file
        heart_rate: Optional test heart rate
        temperature: Optional test temperature
    """
    try:
        data = request.get_json()
        
        from ai_engine.inference_service import StressInferenceService
        
        inference_service = StressInferenceService.get_instance()
        
        if not inference_service.is_model_loaded():
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Train model first using train_ensemble.py'
            }), 503
        
        results = {}
        
        # Test audio if path provided
        if 'test_audio_path' in data:
            audio_path = data['test_audio_path']
            if os.path.exists(audio_path):
                audio_result = inference_service.detect_stress_audio(audio_path)
                results['audio'] = audio_result
        
        # Test physiological if provided
        if 'heart_rate' in data or 'temperature' in data:
            physio_result = inference_service.analyze_physiological(
                heart_rate=data.get('heart_rate'),
                temperature=data.get('temperature')
            )
            results['physiological'] = physio_result
        
        # Test hybrid if both available
        if 'test_audio_path' in data and ('heart_rate' in data or 'temperature' in data):
            audio_path = data['test_audio_path']
            if os.path.exists(audio_path):
                hybrid_result = inference_service.detect_stress_hybrid(
                    audio_path=audio_path,
                    heart_rate=data.get('heart_rate'),
                    temperature=data.get('temperature')
                )
                results['hybrid'] = hybrid_result
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'AI engine not available'
        }), 503
    except Exception as e:
        logger.error(f'Test stress detection error: {e}')
        return jsonify({
            'success': False,
            'error': 'Test failed',
            'message': str(e)
        }), 500