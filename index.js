// Punto de entrada de la aplicación.
import { registerRootComponent } from 'expo';

// Importamos el componente principal
import App from './App';

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
// Registra la app para que funcione en cualquier entorno Expo o build nativo
registerRootComponent(App);
