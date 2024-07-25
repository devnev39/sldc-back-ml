import tensorflow as tf
import tensorflowjs as tfjs
from database.api import read_model_config, read_data_config
from preprocessing.selection import rescale_output

def train_model(model, data):
    model_conf = read_model_config()
    data_conf = read_data_config()
    
    name = model['name']
    model = model['model']

    model.compile(loss='mse', optimizer='adam')

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    '/tmp/model_checkpoint.keras', save_best_only=True, monitor='val_loss', mode='min')

    hist = model.fit(data['X_train'], data['y_train'], epochs=model_conf['epochs'], validation_data=(data['X_val'], data['y_val']), callbacks=[checkpoint_callback], batch_size=model_conf['batch_size'])

    yhat = model.predict(data['X_test'])
    mean = data['train_mean'].to_numpy().reshape(1,-1)[:,0]
    std = data['train_std'].to_numpy().reshape(1,-1)[:,0]

    yhat = rescale_output(yhat, mean, std)

    y_test = rescale_output(data['y_test'], mean, std)

    avg_loss = abs(sum(y_test - yhat)) / len(y_test)
    avg_loss = avg_loss.flatten()

    tfjs.converters.save_keras_model(model, "/tmp/model_checkpoint")

    return {
        "model": model,
        "name": name,
        "mse": sum(hist.history['loss'])/len(hist.history['loss']),
        "val_mse": sum(hist.history['val_loss'])/len(hist.history['val_loss']),
        "epochs": model_conf['epochs'],
        "batch_size": model_conf['batch_size'],
        "window_size": data_conf['window_size'],
        "avg_loss": avg_loss[0],
        "train_data_size": len(data['X_train']),
    }
