#!/usr/bin/env python3
"""
Script para automatizar el manejo de seguidores en GitHub
Funcionalidades:
- Dejar de seguir a usuarios que no te siguen de vuelta
- Seguir a usuarios que te siguen pero tú no los sigues
"""

import os
import time
import requests
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubFollowerManager:
    def __init__(self):
        # Token de GitHub desde variables de entorno
        self.token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME')
        
        # Configuraciones de seguridad
        self.max_unfollows_per_run = int(os.getenv('MAX_UNFOLLOWS_PER_RUN', '20'))
        self.max_follows_per_run = int(os.getenv('MAX_FOLLOWS_PER_RUN', '15'))
        self.delay_between_actions = int(os.getenv('DELAY_SECONDS', '5'))
        
        # Headers para la API de GitHub
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'{self.username}-follower-automation'
        }
        
        # Base URL de la API de GitHub
        self.base_url = 'https://api.github.com'
    
    def get_followers(self, username=None):
        """Obtener lista de seguidores"""
        if not username:
            username = self.username
            
        followers = []
        page = 1
        per_page = 100
        
        logger.info(f"🔍 Obteniendo seguidores de {username}...")
        
        while True:
            url = f"{self.base_url}/users/{username}/followers"
            params = {'page': page, 'per_page': per_page}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                page_followers = response.json()
                if not page_followers:  # No hay más seguidores
                    break
                    
                followers.extend(page_followers)
                logger.info(f"   📄 Página {page}: {len(page_followers)} seguidores")
                page += 1
                time.sleep(1)  # Respeto al rate limit
            else:
                logger.error(f"❌ Error obteniendo seguidores: {response.status_code}")
                logger.error(f"Response: {response.text}")
                break
        
        logger.info(f"✅ Total seguidores: {len(followers)}")
        return followers
    
    def get_following(self, username=None):
        """Obtener lista de usuarios que sigo"""
        if not username:
            username = self.username
            
        following = []
        page = 1
        per_page = 100
        
        logger.info(f"🔍 Obteniendo usuarios que sigue {username}...")
        
        while True:
            url = f"{self.base_url}/users/{username}/following"
            params = {'page': page, 'per_page': per_page}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                page_following = response.json()
                if not page_following:  # No hay más seguidos
                    break
                    
                following.extend(page_following)
                logger.info(f"   📄 Página {page}: {len(page_following)} seguidos")
                page += 1
                time.sleep(1)  # Respeto al rate limit
            else:
                logger.error(f"❌ Error obteniendo seguidos: {response.status_code}")
                logger.error(f"Response: {response.text}")
                break
        
        logger.info(f"✅ Total seguidos: {len(following)}")
        return following
    
    def follow_user(self, username):
        """Seguir a un usuario"""
        url = f"{self.base_url}/user/following/{username}"
        
        response = requests.put(url, headers=self.headers)
        
        if response.status_code == 204:
            logger.info(f"✅ Ahora sigues a @{username}")
            return True
        elif response.status_code == 404:
            logger.warning(f"⚠️  Usuario @{username} no encontrado")
            return False
        else:
            logger.error(f"❌ Error siguiendo a @{username}: {response.status_code}")
            return False
    
    def unfollow_user(self, username):
        """Dejar de seguir a un usuario"""
        url = f"{self.base_url}/user/following/{username}"
        
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 204:
            logger.info(f"✅ Dejaste de seguir a @{username}")
            return True
        elif response.status_code == 404:
            logger.warning(f"⚠️  Usuario @{username} no encontrado o no lo seguías")
            return False
        else:
            logger.error(f"❌ Error dejando de seguir a @{username}: {response.status_code}")
            return False
    
    def check_if_following(self, username):
        """Verificar si sigo a un usuario"""
        url = f"{self.base_url}/user/following/{username}"
        
        response = requests.get(url, headers=self.headers)
        
        return response.status_code == 204
    
    def get_user_info(self, username):
        """Obtener información básica de un usuario"""
        url = f"{self.base_url}/users/{username}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def should_skip_user(self, user_data):
        """Lógica para determinar si saltar un usuario (filtros personalizados)"""
        # Filtros de seguridad
        
        # No dejar de seguir a usuarios muy populares (posibles false positives)
        if user_data.get('followers', 0) > 10000:
            logger.info(f"⏭️  Saltando @{user_data['login']} (usuario popular: {user_data['followers']} seguidores)")
            return True
        
        # No dejar de seguir a organizaciones oficiales de GitHub
        if user_data.get('type') == 'Organization' and 'github' in user_data.get('login', '').lower():
            logger.info(f"⏭️  Saltando @{user_data['login']} (organización GitHub)")
            return True
        
        return False
    
    def follow_back_followers(self):
        """Seguir a usuarios que te siguen pero tú no los sigues"""
        logger.info("🚀 Iniciando proceso: Seguir a seguidores...")
        
        followers = self.get_followers()
        following = self.get_following()
        
        # Crear sets para comparación rápida
        follower_usernames = {user['login'] for user in followers}
        following_usernames = {user['login'] for user in following}
        
        # Usuarios que me siguen pero yo no los sigo
        to_follow_back = follower_usernames - following_usernames
        
        logger.info(f"📊 Análisis de seguidores:")
        logger.info(f"   - Te siguen: {len(follower_usernames)} usuarios")
        logger.info(f"   - Tú sigues: {len(following_usernames)} usuarios")
        logger.info(f"   - Para seguir de vuelta: {len(to_follow_back)} usuarios")
        
        if not to_follow_back:
            logger.info("✨ Ya sigues a todos tus seguidores!")
            return
        
        # Seguir con límites de seguridad
        followed_count = 0
        for username in list(to_follow_back)[:self.max_follows_per_run]:
            if followed_count >= self.max_follows_per_run:
                logger.info(f"⚠️  Límite alcanzado: {self.max_follows_per_run} follows por ejecución")
                break
            
            # Obtener info del usuario para filtros
            user_info = self.get_user_info(username)
            if user_info and self.should_skip_user(user_info):
                continue
            
            if self.follow_user(username):
                followed_count += 1
                time.sleep(self.delay_between_actions)
        
        logger.info(f"✨ Proceso completado. Seguiste a {followed_count} usuarios nuevos.")
    
    def cleanup_non_followers(self):
        """Dejar de seguir a usuarios que no te siguen de vuelta"""
        logger.info("🧹 Iniciando proceso: Limpiar no-seguidores...")
        
        followers = self.get_followers()
        following = self.get_following()
        
        # Crear sets para comparación rápida
        follower_usernames = {user['login'] for user in followers}
        following_usernames = {user['login'] for user in following}
        
        # Usuarios que sigo pero no me siguen de vuelta
        non_followers = following_usernames - follower_usernames
        
        logger.info(f"📊 Análisis de seguidos:")
        logger.info(f"   - Tú sigues: {len(following_usernames)} usuarios")
        logger.info(f"   - Te siguen de vuelta: {len(following_usernames & follower_usernames)} usuarios")
        logger.info(f"   - No te siguen de vuelta: {len(non_followers)} usuarios")
        
        if not non_followers:
            logger.info("✨ Todos los usuarios que sigues te siguen de vuelta!")
            return
        
        # Crear mapa de información de usuarios
        following_info = {user['login']: user for user in following}
        
        # Dejar de seguir con límites de seguridad
        unfollowed_count = 0
        for username in list(non_followers)[:self.max_unfollows_per_run]:
            if unfollowed_count >= self.max_unfollows_per_run:
                logger.info(f"⚠️  Límite alcanzado: {self.max_unfollows_per_run} unfollows por ejecución")
                break
            
            # Aplicar filtros de seguridad
            user_info = following_info.get(username, {})
            if self.should_skip_user(user_info):
                continue
            
            if self.unfollow_user(username):
                unfollowed_count += 1
                time.sleep(self.delay_between_actions)
        
        logger.info(f"✨ Proceso completado. Dejaste de seguir a {unfollowed_count} usuarios.")
    
    def get_statistics(self):
        """Obtener estadísticas actuales"""
        logger.info("📊 Obteniendo estadísticas...")
        
        followers = self.get_followers()
        following = self.get_following()
        
        follower_usernames = {user['login'] for user in followers}
        following_usernames = {user['login'] for user in following}
        
        mutual_follows = follower_usernames & following_usernames
        only_followers = follower_usernames - following_usernames
        only_following = following_usernames - follower_usernames
        
        stats = {
            'followers_count': len(followers),
            'following_count': len(following),
            'mutual_follows': len(mutual_follows),
            'only_followers': len(only_followers),
            'only_following': len(only_following),
            'follow_ratio': len(followers) / max(len(following), 1)
        }
        
        logger.info("📈 Estadísticas actuales:")
        logger.info(f"   - Seguidores: {stats['followers_count']}")
        logger.info(f"   - Siguiendo: {stats['following_count']}")
        logger.info(f"   - Seguimiento mutuo: {stats['mutual_follows']}")
        logger.info(f"   - Solo te siguen: {stats['only_followers']}")
        logger.info(f"   - Solo los sigues: {stats['only_following']}")
        logger.info(f"   - Ratio seguidor/siguiendo: {stats['follow_ratio']:.2f}")
        
        return stats
    
    def run_automation(self, action='both'):
        """Ejecutar la automatización completa"""
        logger.info("🤖 Iniciando automatización de seguidores GitHub...")
        logger.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"👤 Usuario: @{self.username}")
        logger.info(f"🎯 Acción: {action}")
        
        if not self.token or not self.username:
            logger.error("❌ Token de GitHub o username no configurado")
            return
        
        try:
            # Mostrar estadísticas iniciales
            initial_stats = self.get_statistics()
            
            # Ejecutar acciones según el parámetro
            if action in ['both', 'follow_back']:
                logger.info("\n" + "="*50)
                self.follow_back_followers()
                time.sleep(10)  # Pausa entre procesos
            
            if action in ['both', 'cleanup']:
                logger.info("\n" + "="*50)
                self.cleanup_non_followers()
            
            # Mostrar estadísticas finales si se ejecutaron ambas acciones
            if action == 'both':
                logger.info("\n" + "="*50)
                logger.info("📊 ESTADÍSTICAS FINALES:")
                final_stats = self.get_statistics()
                
                # Calcular cambios
                follower_change = final_stats['followers_count'] - initial_stats['followers_count']
                following_change = final_stats['following_count'] - initial_stats['following_count']
                
                logger.info(f"📈 Cambios en esta ejecución:")
                logger.info(f"   - Seguidores: {follower_change:+d}")
                logger.info(f"   - Siguiendo: {following_change:+d}")
            
            logger.info("\n🎉 Automatización completada exitosamente!")
            
        except Exception as e:
            logger.error(f"❌ Error durante la automatización: {str(e)}")
            raise

def main():
    """Función principal"""
    # Configurar desde variables de entorno o argumentos
    action = os.getenv('AUTOMATION_ACTION', 'both')
    
    manager = GitHubFollowerManager()
    
    if not manager.token:
        logger.error("❌ GITHUB_TOKEN no configurado. Agrega tu token de GitHub.")
        logger.error("   Puedes generar uno en: https://github.com/settings/tokens")
        return
    
    if not manager.username:
        logger.error("❌ GITHUB_USERNAME no configurado. Agrega tu username de GitHub.")
        return
    
    # Ejecutar automatización
    manager.run_automation(action)

if __name__ == "__main__":
    main()